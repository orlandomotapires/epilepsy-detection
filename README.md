# eplepsy-detection

A ideia do projeto é utilizar dados de EEG (electro-encefalograma) de pacientes com epilepsia para conseguir classificar em qual fase do ciclo epiléptico aquele comportamento do sinal se encontra. Essa classificação será feita por meio do uso de visão computacional onde um modelo será treinado utilizando sinais de EEG convertidos para imagem utilizando STFT (Short-Time-Fourier-Transform).

A entrada do modelo serão os espectogramas das séries de EEG e a saída esperada é a classificação do modelo em **quatro classes**:

| Classe | Descrição |
|---|---|
| `pre_ictal` | Janela de 90 s imediatamente **antes** do início da crise |
| `ictal` | Janela de 90 s **durante** a crise epiléptica |
| `pos_ictal` | Janela de 90 s imediatamente **após** o fim da crise |
| `normal` | Janela de 90 s de atividade cerebral basal, distante de qualquer crise |

A unidade de análise será o pixel, tendo em vista que estamos tratando com visão computacional. O público interessado e uso pretendido é situado nos seguintes grupos: profissionais da área da saúde, pesquisadores, empresas que têm o objetivo de desenvolver tecnologias embarcadas para realizar essas detecções e também os pacientes com crises epilépticas.

O modelo deve ser avaliado utilizando métricas de sucesso como a capacidade de discernir entre as quatro fases do ciclo epiléptico, sendo a principal métrica a capacidade do modelo de identificar corretamente a fase `ictal` (durante a crise) e distingui-la das demais fases.

É importante citar que apesar de o modelo ser capaz de discernir com precisão considerável entre os casos de epilepsia, a última palavra fica encubida do profissional de sáude responsável e o modelo deve ser utilizado apenas para fins de triagem e aceleração do processo. O modelo não deve ser utilizado como principal fonte de diagnóstico e sim como um auxílio.

Alguns pontos estão fora do escopo do projeto em questão, sendo eles: obtenção do dados e realizar diagnósticos para prescrição de medicamentos.

### Estrutura de Diretórios

**data**
Responsável por armazenar todas as fontes de dados utilizadas neste projeto.

**notebooks**
O espaço de trabalho para a exploração inicial de dados, desenvolvimento e análise do modelo.

**src**
A pasta principal para o código-fonte.

**models**
Uma pasta dedicada para salvar modelos de aprendizado de máquina treinados e pesos após cada execução bem-sucedida de treinamento.

**docs**
O centro de documentação.

| **Etapa e Entregável**        | **Marco do Projeto** |
| ------------------------------------ | -------------------------- |
| README inicial e plano de trabalho   | Projeto definido           |
| Script de download e Data Card v1    | Dados adquiridos           |
| Relatório exploratório             | Base compreendida          |
| annotations.csv e guia de anotação | Rótulos auditados         |
| split_manifest.csv e testes          | Conjuntos protegidos       |
| Pipeline e comparações visuais     | Entrada padronizada        |
| Baseline e política de augmentation | Referência criada         |
| Visualizações e model.summary()    | Modelo projetado           |
| experiments.csv e melhor checkpoint  | Modelo treinado            |
| Relatório de avaliação            | Desempenho explicado       |
| Threshold, incerteza e Grad-CAM      | Saída interpretável      |
| Projeto final e apresentação       | Projeto concluído         |

**Metodologia**

Os dados foram obtidos da base Siena Scalp EEG disponível em [physionet.org/content/siena-scalp-eeg/1.0.0](https://physionet.org/content/siena-scalp-eeg/1.0.0/) e salvos no repositório local. A base contém **13 pacientes utilizados neste projeto** (PN00, PN01, PN03, PN05, PN06, PN07, PN09, PN11, PN12, PN13, PN14, PN16, PN17). O paciente PN10 foi **excluído** por possuir apenas 20 canais EEG, enquanto o padrão dos demais é 29 canais.

Cada paciente possui a gravação de uma ou mais ocorrências de epilepsia. Todas as ocorrências estão registradas em um arquivo chamado `Seizures-list-PNxx.txt`. Esse arquivo segue o seguinte formato:

```
PNxx

Data Sampling Rate: 512 Hz

Channels in EDF files:
Channel 1: Fp1 ... Channel 29: F10
Channel 33: EKG 1 / Channel 34: EKG 2

Seizure n N
File name: PNxx-Y.edf
Registration start time: HH.MM.SS
Registration end time:   HH.MM.SS
Seizure start time:      HH.MM.SS
Seizure end time:        HH.MM.SS
```

**Canais EEG utilizados (29 canais padrão):**

| Ch | Nome | Ch | Nome | Ch | Nome |
|---|---|---|---|---|---|
| 1 | Fp1 | 11 | Cp1 | 21 | O2  |
| 2 | F3  | 12 | Cp5 | 22 | F8  |
| 3 | C3  | 13 | F9  | 23 | T4  |
| 4 | P3  | 14 | Fz  | 24 | T6  |
| 5 | O1  | 15 | Cz  | 25 | Fc2 |
| 6 | F7  | 16 | Pz  | 26 | Fc6 |
| 7 | T3  | 17 | Fp2 | 27 | Cp2 |
| 8 | T5  | 18 | F4  | 28 | Cp6 |
| 9 | Fc1 | 19 | C4  | 29 | F10 |
| 10 | Fc5 | 20 | P4 | — | —  |

> **Nota:** Os canais EKG (33 e 34) são ignorados no pré-processamento.

**Segmentação temporal (janela fixa de 90 s):**

Cada gravação EDF é fatiada em exatamente 4 segmentos de **90 segundos (46.080 amostras a 512 Hz)** por ocorrência de crise:

| Classe | Início | Fim |
|---|---|---|
| `pre_ictal`  | `seizure_start − 90 s` | `seizure_start` |
| `ictal`      | `seizure_start` | `seizure_start + 90 s` |
| `pos_ictal`  | `seizure_end` | `seizure_end + 90 s` |
| `normal`     | Segmento basal distante ≥ 30 min de qualquer crise | mesmo + 90 s |

O pré-processamento é realizado no notebook `notebooks/00_data_conversion.ipynb`, que recebe como entrada a pasta `physionet.org/files` e gera os espectogramas STFT em `data/processed/spectrograms/`, organizados por paciente e nomeados conforme o arquivo EDF de origem (ex: `PN00-1_ictal.png`).

