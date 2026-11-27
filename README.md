# epilepsy-detection

Classificação da fase do ciclo epiléptico a partir de espectrogramas de EEG, com redes neurais convolucionais.

## Objetivo

O projeto investiga se uma rede convolucional consegue dizer em que fase do ciclo epiléptico está uma janela de 90 s de EEG de escalpo. O sinal de cada janela é convertido em imagem por STFT (*Short-Time Fourier Transform*) e a rede classifica a imagem em **quatro classes**:

| Classe | Descrição |
|---|---|
| `PRE_ICTAL` | Janela de 90 s imediatamente **antes** da crise |
| `ICTAL` | Janela de 90 s **durante** a crise (centrada no meio dela) |
| `POS_ICTAL` | Janela de 90 s imediatamente **depois** da crise |
| `NORMAL` | Janela de 90 s de atividade basal, longe de qualquer crise |

A métrica mais importante é a capacidade de reconhecer a fase `ICTAL` e separá-la das demais.

**Uso pretendido:** apoio à triagem para profissionais de saúde, pesquisadores e empresas que desenvolvem detecção embarcada. O modelo **não é ferramenta de diagnóstico**; a decisão fica com o profissional de saúde. Aquisição de dados e prescrição de medicamentos estão fora do escopo.

## Base de dados

[Siena Scalp EEG Database](https://physionet.org/content/siena-scalp-eeg/1.0.0/) (PhysioNet, v1.0.0): EEG de 14 pacientes adultos, 512 Hz, sistema 10-20. Detalhes no [Data Card](docs/data_card.md).

| Item | Valor |
|---|---|
| Pacientes usados | 12 (PN10 excluído por ter 20 canais; PN01 sem EDF utilizável) |
| Imagens válidas | **137** espectrogramas RGB de 359 x 129 px (tempo x frequência) |
| Imagens por classe | 34–35 (`ICTAL` 34, `NORMAL` 35, `POS_ICTAL` 34, `PRE_ICTAL` 34) |
| Canais RGB | média dos espectrogramas dos eletrodos frontais (R), centrais (G) e parietais (B) |
| Pré-processamento | CLAHE + ajuste de contraste, redimensionamento para 224 x 224 e normalização em [0, 1] |

**Divisão treino / validação / teste**, por paciente (nenhum paciente aparece em dois conjuntos):

| Conjunto | Pacientes | Imagens únicas | Imagens usadas | Por classe |
|---|---|---|---|---|
| Treino | PN00, PN03, PN05, PN06, PN07, PN11, PN12, PN14 | 97 | 100 (oversampling de 3) | 25 |
| Validação | PN09, PN16 | 20 | 20 | 5 |
| Teste | PN13, PN17 | 20 | 20 | 5 |

A divisão está em [data/annotations/splits.csv](data/annotations/splits.csv).

## Modelo

A CNN tem três blocos convolucionais e uma cabeça densa:

| Camada | Saída | Parâmetros |
|---|---|---|
| Input | 224 x 224 x 3 | 0 |
| Conv2D 32 (3x3, ReLU) + MaxPooling 2x2 | 112 x 112 x 32 | 896 |
| Conv2D 64 (3x3, ReLU) + MaxPooling 2x2 | 56 x 56 x 64 | 18.496 |
| Conv2D 128 (3x3, ReLU) — `conv2d_2` + MaxPooling 2x2 | 28 x 28 x 128 | 73.856 |
| Flatten | 100.352 | 0 |
| Dense 128 (ReLU) + Dropout 0,5 | 128 | 12.845.184 |
| Dense 4 (Softmax) | 4 | 516 |
| **Total** | | **12.938.948** |

**Parâmetros de treinamento**

| Parâmetro | Valor |
|---|---|
| Otimizador | Adam (taxa de aprendizado padrão, 0,001) |
| Função de perda | `sparse_categorical_crossentropy` |
| Épocas | 30 |
| Batch size | 32 (padrão do Keras) |
| Seed | 0 (`tf.keras.utils.set_random_seed`) |
| Augmentation | nenhum |

Para comparação, foram treinados mais dois modelos com o **mesmo extrator convolucional** e os mesmos parâmetros de treino:

- **FCNN** (110.276 parâmetros): troca `Flatten` + `Dense` por convoluções 1x1 e `GlobalAveragePooling2D`.
- **Encoder-Decoder** (337.828 parâmetros): acrescenta três `Conv2DTranspose` depois do extrator e usa a cabeça da FCNN.

## Resultados

Conjunto de teste (20 imagens, 5 por classe). Precisão, recall e F1 são a média macro das 4 classes. O acaso fica em 0,25.

| Modelo | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| CNN | 0,15 | 0,10 | 0,15 | 0,12 |
| **FCNN** | **0,40** | **0,53** | **0,40** | **0,38** |
| Encoder-Decoder | 0,25 | 0,06 | 0,25 | 0,10 |

- **CNN:** overfitting. Chega a 97% de acurácia no treino e fica em 40% na validação e 15% no teste. Com 12,9 milhões de parâmetros e 100 imagens, a rede decora o treino.
- **FCNN:** o melhor modelo, mas ainda fraco. Na classe `ICTAL` tem precisão 1,00 e recall 0,20 (acerta 1 de 5 crises e não dá falso alarme).
- **Encoder-Decoder:** prevê `NORMAL` para todas as imagens.

**Interpretabilidade (Grad-CAM, camada `conv2d_2`).** A CNN olha para as baixas frequências (0–10 Hz) e para rajadas curtas de banda larga, sem um padrão consistente por classe. A FCNN e o Encoder-Decoder dão muito peso à linha de **50 Hz**, que é ruído da rede elétrica e varia por paciente, não por fase da crise. A análise completa está em [notebooks/07_gradcam.ipynb](notebooks/07_gradcam.ipynb) e as figuras em [docs/gradcam_figures/](docs/gradcam_figures/).

**Próximos passos:** filtrar 50 Hz e harmônicos (ou limitar o espectrograma a ~45 Hz), aumentar os dados e usar validação *leave-one-patient-out*.

## Estrutura do projeto

```
epilepsy-detection/
├── data/
│   ├── annotations/        # annotations.csv (janelas e status), splits.csv (divisão), modifications.csv (realce)
│   └── processed/
│       ├── spectrograms/       # espectrogramas STFT gerados a partir do EDF
│       └── mod_spectograms/    # espectrogramas com CLAHE + contraste (entrada dos modelos)
├── docs/
│   ├── data_card.md        # descrição da base e do conjunto de imagens
│   ├── eda_report.md       # relatório da análise exploratória
│   ├── eda_figures/        # figuras da análise exploratória
│   └── gradcam_figures/    # galerias e mapas médios do Grad-CAM
├── models/                 # modelos treinados (.keras, fora do git)
├── notebooks/
│   ├── 00_data_conversion.ipynb                 # EDF → janelas de 90 s → espectrogramas
│   ├── 01_exploratory_analysis.ipynb            # análise exploratória
│   ├── 02_split_balance.ipynb                   # divisão por paciente e oversampling
│   ├── 03_image_enhancement.ipynb               # CLAHE + contraste
│   ├── 04_convolutional_filters.ipynb           # filtros convolucionais 3x3 aplicados à mão
│   ├── 05_cnn_classification.ipynb              # treino da CNN
│   ├── 05_fcnn_classification.ipynb             # treino da FCNN
│   ├── 05_encoder_decoder_classification.ipynb  # treino do Encoder-Decoder
│   ├── 06_metrics.ipynb                         # avaliação no teste
│   └── 07_gradcam.ipynb                         # Grad-CAM e interpretação
├── src/preprocessing/      # leitura de EDF, segmentação, STFT, realce e filtros
├── physionet.org/          # dados brutos baixados (fora do git)
└── requirements.txt
```

## Como reproduzir

1. Crie o ambiente (Python 3.11) e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Baixe a base para a raiz do projeto (~13 GB):
   ```bash
   wget -r -N -c -np https://physionet.org/files/siena-scalp-eeg/1.0.0/
   ```
3. Rode os notebooks na ordem numérica, de `00` a `07`. Os notebooks `05` salvam os modelos em `models/`, que os notebooks `06` e `07` carregam.

Os espectrogramas e o `splits.csv` já estão versionados, então para treinar e avaliar basta começar no `05`.

## Licença

Código sob licença MIT ([LICENSE](LICENSE)). A base Siena Scalp EEG é distribuída sob CC BY 4.0; cite Detti (2020) e o PhysioNet ao usar os dados (veja o [Data Card](docs/data_card.md#12-citações)).
