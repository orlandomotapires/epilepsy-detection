# Data Card — Siena Scalp EEG Database
**Versão:** 1.0  
**Criado em:** 2026-09-07  
**Projeto:** epilepsy-detection  

---

## 1. Identificação do Dataset

| Campo | Valor |
|---|---|
| **Nome** | Siena Scalp EEG Database |
| **Versão** | 1.0.0 |
| **DOI (v1.0.0)** | [10.13026/5d4a-j060](https://doi.org/10.13026/5d4a-j060) |
| **DOI (latest)** | [10.13026/s309-a395](https://doi.org/10.13026/s309-a395) |
| **URL** | https://physionet.org/content/siena-scalp-eeg/1.0.0/ |
| **Plataforma** | PhysioNet |
| **Tipo** | Database — Open Access |
| **Tamanho total** | 20,3 GB (descomprimido) / 13,0 GB (ZIP) |

---

## 2. Autor e Provedor

| Campo | Valor |
|---|---|
| **Autor principal** | Paolo Detti |
| **Afiliação** | Department of Information Engineering and Mathematics, University of Siena, Itália |
| **Instituição coletora** | Unit of Neurology and Neurophysiology — University of Siena |
| **Projeto de origem** | PANACEE — desenvolvimento de dispositivos não invasivos de baixo custo para predição de crises epilépticas |
| **Publicação associada** | Detti, P., Vatti, G., Zabalo Manrique de Lara, G. *EEG Synchronization Analysis for Seizure Prediction: A Study on Data of Noninvasive Recordings.* Processes 2020, 8(7), 846. [doi:10.3390/pr8070846](https://doi.org/10.3390/pr8070846) |

---

## 3. Datas e Acesso

| Campo | Valor |
|---|---|
| **Data de publicação** | 11 de agosto de 2020 |
| **Data de acesso (este projeto)** | Setembro de 2026 |
| **Política de acesso** | Acesso livre — qualquer pessoa pode acessar os arquivos, desde que em conformidade com a licença |

---

## 4. Licença

| Campo | Valor |
|---|---|
| **Licença** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |
| **Texto completo** | `physionet.org/files/siena-scalp-eeg/1.0.0/LICENSE.txt` |
| **Permite** | Reprodução, distribuição, adaptação e uso comercial |
| **Requer** | Atribuição ao autor original (Paolo Detti / PhysioNet) |
| **Citação obrigatória** | `Detti, P. (2020). Siena Scalp EEG Database (version 1.0.0). PhysioNet. https://doi.org/10.13026/5d4a-j060` |

---

## 5. Finalidade Declarada

> *"The database consists of EEG recordings of 14 patients acquired at the Unit of Neurology and Neurophysiology of the University of Siena. The data has been collected during a regional research project (PANACEE) aiming at the development of noninvasive patient-specific monitoring/control low-cost devices for the prediction of epileptic seizures."*
> — Descrição oficial, PhysioNet

**Objetivo original:** Desenvolvimento e validação de algoritmos de **predição de crises epilépticas** a partir de dados de EEG não invasivo.

**Problema investigável:** Detecção e/ou predição de crises epilépticas (seizure detection / seizure prediction) usando sinais de EEG escalp.

**Domínio de aplicação:** Neurologia clínica, dispositivos médicos embarcados, aprendizado de máquina aplicado à saúde.

---

## 6. Descrição dos Dados

### 6.1 Visão Geral

| Atributo | Valor |
|---|---|
| **Nº de pacientes (original)** | 14 |
| **Nº de pacientes utilizados neste projeto** | 13 (PN10 excluído) |
| **Total de crises (dataset completo)** | 47 crises |
| **Tempo total de gravação** | ~128 horas |
| **Formato dos arquivos** | EDF (European Data Format) |
| **Taxa de amostragem** | 512 Hz |
| **Sistema de eletrodos** | International 10-20 System |

### 6.2 Pacientes

| Paciente | Sexo | Idade | Tipo de Crise | Lateralização | Canais EEG | Nº Crises | Tempo Grav. (min) |
|---|---|---|---|---|---|---|---|
| PN00 | M | 55 | IAS | T-R | 29 | 5 | 198 |
| PN01 | M | 46 | IAS | T-L | 29 | 2 | 809 |
| PN03 | M | 54 | IAS | T-R | 29 | 2 | 752 |
| PN05 | F | 51 | IAS | T-L | 29 | 3 | 359 |
| PN06 | M | 36 | IAS | T-L | 29 | 5 | 722 |
| PN07 | F | 20 | IAS | T-L | 29 | 1 | 523 |
| PN09 | F | 27 | IAS | T-L | 29 | 3 | 410 |
| ~~PN10~~ | ~~M~~ | ~~25~~ | ~~FBTC~~ | ~~F-Bilateral~~ | ~~20~~ | ~~10~~ | ~~1002~~ |
| PN11 | F | 58 | IAS | T-R | 29 | 1 | 145 |
| PN12 | M | 71 | IAS | T-L | 29 | 4 | 246 |
| PN13 | F | 34 | IAS | T-L | 29 | 3 | 519 |
| PN14 | M | 49 | WIAS | T-L | 29 | 4 | 1408 |
| PN16 | F | 41 | IAS | T-L | 29 | 2 | 303 |
| PN17 | M | 42 | IAS | T-R | 29 | 2 | 308 |

> **Legendas de tipo de crise (ILAE):**  
> `IAS` = Focal onset with Impaired Awareness Seizure  
> `WIAS` = Focal onset Without Impaired Awareness Seizure  
> `FBTC` = Focal to Bilateral Tonic-Clonic  
> `T` = Temporal · `R` = Right · `L` = Left · `F` = Frontal

**Distribuição de sexo:** 9 homens (idades 25–71) · 5 mulheres (idades 20–58)

### 6.3 Equipamentos Utilizados

| Item | Detalhe |
|---|---|
| **Amplificadores** | EB Neuro e Natus Quantum LTM |
| **Eletrodos** | Prata/ouro reutilizáveis (cup electrodes) |
| **Sistema de aquisição** | Video-EEG |
| **Posição do paciente** | Deitado (dormindo ou acordado) |

### 6.4 Canais EEG (29 canais padrão utilizados neste projeto)

| Ch | Nome | Ch | Nome | Ch | Nome |
|---|---|---|---|---|---|
| 1 | Fp1 | 11 | Cp1 | 21 | O2 |
| 2 | F3 | 12 | Cp5 | 22 | F8 |
| 3 | C3 | 13 | F9 | 23 | T4 |
| 4 | P3 | 14 | Fz | 24 | T6 |
| 5 | O1 | 15 | Cz | 25 | Fc2 |
| 6 | F7 | 16 | Pz | 26 | Fc6 |
| 7 | T3 | 17 | Fp2 | 27 | Cp2 |
| 8 | T5 | 18 | F4 | 28 | Cp6 |
| 9 | Fc1 | 19 | C4 | 29 | F10 |
| 10 | Fc5 | 20 | P4 | — | *(ignorado: EKG)* |

> **Ignorados:** Channel 33 (EKG 1) e Channel 34 (EKG 2)

---

## 7. Classes de Segmentação (definidas neste projeto)

O dataset original não provê rótulos de segmentação temporal — as anotações são apenas os tempos de início e fim de cada crise. As **4 classes abaixo foram definidas para este projeto** com base nas anotações do `Seizures-list-PNxx.txt`:

| Classe | Descrição | Janela |
|---|---|---|
| `pre_ictal` | Imediatamente **antes** do início da crise | 90 s → `seizure_start` |
| `ictal` | **Durante** a crise epiléptica | `seizure_start` → `seizure_start + 90 s` |
| `pos_ictal` | Imediatamente **após** o fim da crise | `seizure_end` → `seizure_end + 90 s` |
| `normal` | Atividade cerebral basal, distante >= 30 min de qualquer crise | 90 s de região basal |

**Parâmetros de segmentação:**
- Janela temporal: **90 segundos** (fixo)
- Amostras por janela: **46.080** (90 s × 512 Hz)
- Shape de cada segmento: `(29 canais, 46.080 amostras)`

---

## 8. Limitações Conhecidas

- **Desequilíbrio de classes:** A classe `normal` tem potencial muito maior de amostras disponíveis do que as demais. Estratégias de balanceamento serão necessárias.
- **PN10 excluído:** O paciente PN10 possui apenas 20 canais EEG (vs. 29 dos demais) e foi excluído para manter uniformidade do input.
- **Datas anonimizadas:** Todas as datas nos arquivos `.edf` foram de-identificadas. As marcações de tempo são relativas, não absolutas.
- **Tipo dominante de crise:** A grande maioria dos pacientes apresenta `IAS` de origem temporal. O dataset não representa uniformemente todos os tipos de epilepsia — resultados podem não generalizar para outros tipos.
- **Amostras por paciente variáveis:** PN07 e PN11 têm apenas 1 crise cada, enquanto PN06 e PN00 têm 5. Há desequilíbrio também entre pacientes.
- **Segmentos parcialmente inviáveis:** Alguns segmentos `pre_ictal` ou `pos_ictal` podem não ter 90 s disponíveis (gravação muito próxima da crise). Nesses casos, o segmento será marcado como `skipped` no `annotations.csv`.
- **Uso clínico proibido:** Este dataset é destinado a fins de pesquisa. O modelo resultante **não deve ser utilizado como ferramenta diagnóstica principal**.

---

## 9. Ética e Conformidade

- Aprovação pelo **Comitê de Ética da Universidade de Siena**, em conformidade com a Declaração de Helsinki.
- Cada paciente assinou **termo de consentimento informado** autorizando a gravação em vídeo e o uso dos dados para divulgação científica.
- Todos os dados foram **anonimizados** antes da publicação (datas removidas dos arquivos EDF).

---

## 10. Recomendações de Uso

- **Sempre citar** o autor original (Detti, 2020) e a plataforma PhysioNet ao publicar resultados.
- Utilizar o dataset apenas para fins de **triagem e pesquisa**, nunca como diagnóstico definitivo.
- Ao dividir treino/validação/teste, **nunca misturar pacientes** entre os conjuntos (divisão por paciente, não por amostra), para evitar data leakage.
- Considerar avaliação **leave-one-patient-out** para estimar generalização real do modelo.
- Monitorar métricas separadas por tipo de crise (`IAS`, `WIAS`, `FBTC`) para identificar possíveis vieses.

---

## 11. Respostas à Análise Inicial

| Pergunta | Resposta |
|---|---|
| **Nome da base** | Siena Scalp EEG Database |
| **Autor / Provedor** | Paolo Detti — Dept. of Information Engineering and Mathematics, University of Siena |
| **Origem original dos dados** | Unit of Neurology and Neurophysiology, University of Siena, Itália |
| **Objetivo declarado** | Desenvolvimento de dispositivos não invasivos de baixo custo para predição de crises epilépticas (projeto PANACEE) |
| **Problema investigável** | Predição e/ou detecção de crises epilépticas via análise de EEG escalp |
| **Domínio** | Neurologia clínica / Dispositivos médicos / Machine Learning em saúde |
| **Classes neste projeto** | `pre_ictal`, `ictal`, `pos_ictal`, `normal` (definidas a partir das anotações do dataset) |
| **Informações de pacientes** | Sim — `subject_info.csv`: sexo, idade, classificação ILAE, canais, nº crises, tempo de gravação |
| **Informações de hospital / equipamento** | Sim — Univ. de Siena; amplificadores EB Neuro e Natus Quantum LTM; eletrodos prata/ouro |
| **Limitações / recomendações** | Dataset de pesquisa, não diagnóstico; aprovação ética da Univ. de Siena; consentimento informado; CC BY 4.0 exige atribuição |

---

## 12. Citações

### Dataset

```bibtex
@article{PhysioNet-siena-scalp-eeg-1.0.0,
  author  = {Detti, Paolo},
  title   = {{Siena Scalp EEG Database}},
  journal = {{PhysioNet}},
  year    = {2020},
  month   = aug,
  note    = {Version 1.0.0},
  doi     = {10.13026/5d4a-j060},
  url     = {https://doi.org/10.13026/5d4a-j060}
}
```

### Publicação associada

```bibtex
@article{detti2020eeg,
  author  = {Detti, Paolo and Vatti, Giampaolo and {Zabalo Manrique de Lara}, Gonzalo},
  title   = {EEG Synchronization Analysis for Seizure Prediction: A Study on Data of Noninvasive Recordings},
  journal = {Processes},
  volume  = {8},
  number  = {7},
  pages   = {846},
  year    = {2020},
  doi     = {10.3390/pr8070846}
}
```

### Plataforma PhysioNet

```bibtex
@article{pollard_physionet_2026,
  author  = {Pollard, Tom and Moody, Benjamin E. and Lehman, Li-wei H. and others},
  title   = {{PhysioNet} as a global platform for biomedical research},
  journal = {Nature Health},
  year    = {2026},
  doi     = {10.1038/s44360-026-00096-z}
}
```
