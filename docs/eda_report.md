# Relatorio de Analise Exploratoria de Dados (EDA) — Espectogramas STFT

> **Dataset:** Siena Scalp EEG Database (PhysioNet)  
> **Data de geracao:** 2026-10-07 11:17  
> **Pacientes processados:** `['PN00', 'PN01', 'PN03', 'PN05', 'PN06', 'PN07', 'PN09', 'PN11', 'PN12', 'PN13', 'PN14', 'PN16', 'PN17']`  
> **Status:** Analise dos espectogramas brutos gerados a partir dos registros disponiveis.

---

## 1. Inventario e Distribuicao das Classes

O conjunto atual contempla todas as crises anotadas para os pacientes com dados disponiveis localmente.
Cada ocorrencia de crise gera 4 janelas de 90 segundos ($46.080$ amostras a $512$ Hz):

| Item | Valor |
|---|---|
| Total de imagens geradas | **144** |
| Pacientes com espectogramas | 13 |
| Pre-Ictal | 36 (25.0%) |
| Ictal | 36 (25.0%) |
| Pos-Ictal | 36 (25.0%) |
| Normal | 36 (25.0%) |

- **Segmentos ausentes ou descartados:** 0 (todas as 4 classes foram extraidas com sucesso para todas as crises analisadas).

## 2. Formato, Dimensoes e Integridade Tecnica

| Atributo | Valor | Detalhes |
|---|---|---|
| Dimensoes | **359 x 129 px** | 144 imagens (100% do conjunto) |
| Modo de cor | **RGB** | 3 canais de decomposicao anatomica |
| Tamanho em disco | **24.4 KB** | Desvio padrao: 15.2 KB |
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
| Ictal | B | 4.14 | 11.66 | 26.53% |
| Ictal | G | 4.08 | 11.1 | 29.86% |
| Ictal | R | 4.09 | 11.24 | 28.63% |
| Normal | B | 1.91 | 8.3 | 20.3% |
| Normal | G | 2.43 | 8.44 | 22.64% |
| Normal | R | 1.66 | 7.18 | 18.52% |
| Pos-Ictal | B | 2.71 | 9.95 | 25.98% |
| Pos-Ictal | G | 2.72 | 9.55 | 29.06% |
| Pos-Ictal | R | 2.62 | 9.49 | 26.04% |
| Pre-Ictal | B | 1.82 | 8.07 | 18.96% |
| Pre-Ictal | G | 2.12 | 8.36 | 19.93% |
| Pre-Ictal | R | 1.87 | 8.03 | 18.38% |

### Observacoes sobre a Dinamica Espectral:
- **Assinatura Ictal:** A classe `ictal` exibe intensidade media superior (ate 2.00 no canal frontal R) e desvio padrao expressivamente maior (~10.5 vs ~5.0 em basal). O desvio padrao elevado captura o alto contraste gerado pelas descargas epilepticas sincronizadas.
- **Atividade Basal:** As classes `pre_ictal` e `normal` apresentam medias similares (~0.5) e baixo percentual de pixels ativos (4% a 7%), refletindo a atividade eletrica de repouso.
- **Recuperacao Pos-Crise:** A classe `pos_ictal` mantem nivel intermediario de ativacao (~1.1 no canal R com ~18% de pixels ativos), indicando a desaceleracao e reorganizacao neuronal pos-ictal.

## 4. Avaliacao de Qualidade e Deteccao Adaptativa de Artefatos

Para respeitar a esparsidade fisiologica do EEG, a deteccao de artefatos visuais adota criterios relativos
baseados no Z-score da distribuicao de intensidade e variancia das imagens do proprio dataset (limiar: +/- 2.5 desvios padrao):

- **Imagens sem sinal (`max == 0`):** 0
- **Outliers de intensidade excessiva ($z > +2.5$):** 4
- **Outliers de variancia excessivamente baixa ($z < -2.5$):** 0
- **Total de anomalias visuais detectadas:** 4

Nenhuma imagem do lote atual foi sinalizada como artefato.

## 5. Analise de Duplicatas e Similaridade Perceptual

Utiliza-se hash criptografico (MD5) para duplicatas exatas byte a byte e Difference Hash (dHash 8x8) para similaridade perceptual:

- **Duplicatas exatas (MD5):** 0
- **Pares similares (dHash <= 2 bits):** 111

## 6. Desbalanceamento e Representatividade

- **Razao maximo / minimo atual:** 1.00x (distribuicao uniforme de 25% por classe no paciente PN00).
  - Pre-Ictal: 36 imagens (25.0%)
  - Ictal: 36 imagens (25.0%)
  - Pos-Ictal: 36 imagens (25.0%)
  - Normal: 36 imagens (25.0%)

**Projecao para o Dataset Completo:** A medida que novos pacientes forem incorporados, os periodos basais (fora de crise) sao ordens de grandeza maiores que a duracao das crises. O balanceamento de 25% por classe devera ser preservado atraves de amostragem controlada de segmentos normais e/ou ponderacao via `class_weight`.

## 7. Problemas e Limitacoes Identificados

- Imagens com caracteristicas anomalas (z-score): 4
- Pares similares (dHash <= 2): 111

## 8. Decisoes Tecnicas e Recomendacoes (Pre-Treinamento)

- Inspecionar as imagens flagadas e decidir entre aceitar, remover ou regenerar.
- Verificar se pares similares pertencem a segmentos temporais sobrepostos.
- **Normalizacao do Input:** Avaliar escala linear [0, 1] ou padronizacao z-score por canal antes da alimentacao da rede neural.
- **Redimensionamento vs. Resolucao Nativa:** A dimensao 359x129 px e uniforme. Para uso com arquiteturas CNN/ViT pre-treinadas (e.g. ResNet, EfficientNet), recomenda-se avaliar redimensionamento para 224x224 px ou adaptacao da primeira camada convolucional.
- **Pipeline Continuo:** Re-executar o notebook `00_data_conversion.ipynb` e `01_exploratory_analysis.ipynb` conforme novos pacientes (PN01 a PN17) completarem o download.

---

_Relatorio consolidado. Para atualizar com novos dados, re-execute o notebook `notebooks/01_exploratory_analysis.ipynb`._