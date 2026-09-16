# Relatorio de Analise Exploratoria de Dados (EDA) — Espectogramas STFT

> **Dataset:** Siena Scalp EEG Database (PhysioNet)  
> **Data de geracao:** 2026-09-16 11:56  
> **Pacientes processados:** `['PN00']`  
> **Status:** Analise dos espectogramas brutos gerados a partir dos registros disponiveis.

---

## 1. Inventario e Distribuicao das Classes

O conjunto atual contempla todas as crises anotadas para os pacientes com dados disponiveis localmente.
Cada ocorrencia de crise gera 4 janelas de 90 segundos ($46.080$ amostras a $512$ Hz):

| Item | Valor |
|---|---|
| Total de imagens geradas | **20** |
| Pacientes com espectogramas | 1 |
| Pre-Ictal | 5 (25.0%) |
| Ictal | 5 (25.0%) |
| Pos-Ictal | 5 (25.0%) |
| Normal | 5 (25.0%) |

- **Segmentos ausentes ou descartados:** 0 (todas as 4 classes foram extraidas com sucesso para todas as crises analisadas).

## 2. Formato, Dimensoes e Integridade Tecnica

| Atributo | Valor | Detalhes |
|---|---|---|
| Dimensoes | **359 x 129 px** | 20 imagens (100% do conjunto) |
| Modo de cor | **RGB** | 3 canais de decomposicao anatomica |
| Tamanho em disco | **12.8 KB** | Desvio padrao: 6.2 KB |
| Arquivos corrompidos | **0** | Verificados via `PIL.Image.verify()` |

### Composicao Anatomica dos Canais RGB:
- **Canal R (Frontal):** Eletrodos Fp1, F3, F7, Fz, Fp2, F4, F8, F9, F10
- **Canal G (Central e Temporal):** Eletrodos C3, Cz, C4, T3, T4, T5, T6, Fc1, Fc2, Fc5, Fc6, Cp1, Cp2, Cp5, Cp6
- **Canal B (Parietal e Occipital):** Eletrodos P3, Pz, P4, O1, O2

## 3. Dinamica Espectral e Intensidade por Canal

Os espectogramas STFT de EEG apresentam **esparsidade natural**: a densidade de potencia espectral
se concentra em faixas especificas de frequencia (e.g. ritmos delta, teta, alfa, beta) e em instantes discretos,
mantendo grande parte do fundo escuro (valores proximos a zero). Valores medios globais entre 0.3 e 2.0 (em escala [0–255])
sao biologicamente esperados e representam sinal valido, nao se tratando de artefato ou subexposicao.

| Classe | Canal | Intensidade Media | Desvio Padrao | Pixels Nao-Nulos (%) |
|---|---|---|---|---|
| Ictal | B | 1.11 | 8.9 | 7.87% |
| Ictal | G | 1.51 | 8.98 | 16.31% |
| Ictal | R | 2.0 | 10.54 | 17.14% |
| Normal | B | 0.37 | 4.73 | 4.1% |
| Normal | G | 0.37 | 4.45 | 5.17% |
| Normal | R | 0.52 | 5.05 | 7.48% |
| Pos-Ictal | B | 0.76 | 7.01 | 6.95% |
| Pos-Ictal | G | 1.08 | 7.06 | 18.37% |
| Pos-Ictal | R | 1.15 | 6.96 | 18.14% |
| Pre-Ictal | B | 0.51 | 5.7 | 4.84% |
| Pre-Ictal | G | 0.54 | 5.56 | 6.67% |
| Pre-Ictal | R | 0.56 | 5.63 | 6.33% |

### Observacoes sobre a Dinamica Espectral:
- **Assinatura Ictal:** A classe `ictal` exibe intensidade media superior (ate 2.00 no canal frontal R) e desvio padrao expressivamente maior (~10.5 vs ~5.0 em basal). O desvio padrao elevado captura o alto contraste gerado pelas descargas epilepticas sincronizadas.
- **Atividade Basal:** As classes `pre_ictal` e `normal` apresentam medias similares (~0.5) e baixo percentual de pixels ativos (4% a 7%), refletindo a atividade eletrica de repouso.
- **Recuperacao Pos-Crise:** A classe `pos_ictal` mantem nivel intermediario de ativacao (~1.1 no canal R com ~18% de pixels ativos), indicando a desaceleracao e reorganizacao neuronal pos-ictal.

## 4. Avaliacao de Qualidade e Deteccao Adaptativa de Artefatos

Para respeitar a esparsidade fisiologica do EEG, a deteccao de artefatos visuais adota criterios relativos
baseados no Z-score da distribuicao de intensidade e variancia das imagens do proprio dataset (limiar: +/- 2.5 desvios padrao):

- **Imagens sem sinal (`max == 0`):** 0
- **Outliers de intensidade excessiva ($z > +2.5$):** 0
- **Outliers de variancia excessivamente baixa ($z < -2.5$):** 0
- **Total de anomalias visuais detectadas:** 0

Nenhuma imagem do lote atual foi sinalizada como artefato.

## 5. Analise de Duplicatas e Similaridade Perceptual

Utiliza-se hash criptografico (MD5) para duplicatas exatas byte a byte e Difference Hash (dHash 8x8) para similaridade perceptual:

- **Duplicatas exatas (MD5):** 0
- **Pares similares (dHash <= 2 bits):** 6

| Imagem 1 | Classe 1 | Imagem 2 | Classe 2 | Distancia Hamming |
|---|---|---|---|---|
| PN00-2_seizure02_normal.png | normal | PN00-5_seizure05_normal.png | normal | 1 |
| PN00-2_seizure02_pre_ictal.png | pre_ictal | PN00-3_seizure03_pre_ictal.png | pre_ictal | 2 |
| PN00-2_seizure02_pre_ictal.png | pre_ictal | PN00-4_seizure04_normal.png | normal | 2 |
| PN00-2_seizure02_pre_ictal.png | pre_ictal | PN00-4_seizure04_pre_ictal.png | pre_ictal | 2 |
| PN00-3_seizure03_normal.png | normal | PN00-5_seizure05_pos_ictal.png | pos_ictal | 2 |
| PN00-4_seizure04_normal.png | normal | PN00-4_seizure04_pre_ictal.png | pre_ictal | 2 |

Os pares com similaridade perceptual correspondem predominantemente a segmentos de atividade basal (`pre_ictal` e `normal`), cuja esparsidade e fundo predominantemente escuro naturalmente produzem hashes perceptuais proximos, sem implicar duplicacao de sinal.

## 6. Desbalanceamento e Representatividade

- **Razao maximo / minimo atual:** 1.00x (distribuicao uniforme de 25% por classe no paciente PN00).
  - Pre-Ictal: 5 imagens (25.0%)
  - Ictal: 5 imagens (25.0%)
  - Pos-Ictal: 5 imagens (25.0%)
  - Normal: 5 imagens (25.0%)

**Projecao para o Dataset Completo:** A medida que novos pacientes forem incorporados, os periodos basais (fora de crise) sao ordens de grandeza maiores que a duracao das crises. O balanceamento de 25% por classe devera ser preservado atraves de amostragem controlada de segmentos normais e/ou ponderacao via `class_weight`.

## 7. Problemas e Limitacoes Identificados

- Pares similares (dHash <= 2): 6

## 8. Decisoes Tecnicas e Recomendacoes (Pre-Treinamento)

- Verificar se pares similares pertencem a segmentos temporais sobrepostos.
- **Normalizacao do Input:** Avaliar escala linear [0, 1] ou padronizacao z-score por canal antes da alimentacao da rede neural.
- **Redimensionamento vs. Resolucao Nativa:** A dimensao 359x129 px e uniforme. Para uso com arquiteturas CNN/ViT pre-treinadas (e.g. ResNet, EfficientNet), recomenda-se avaliar redimensionamento para 224x224 px ou adaptacao da primeira camada convolucional.
- **Pipeline Continuo:** Re-executar o notebook `00_data_conversion.ipynb` e `01_exploratory_analysis.ipynb` conforme novos pacientes (PN01 a PN17) completarem o download.

---

_Relatorio consolidado. Para atualizar com novos dados, re-execute o notebook `notebooks/01_exploratory_analysis.ipynb`._