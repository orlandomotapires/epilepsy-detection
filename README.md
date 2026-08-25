# eplepsy-detection

A ideia do projeto é utilizar dados de EEG (electro-encefalograma) de pacientes com epilepsia para conseguir classificar se aquele comportamento do sinal apresenta caracteristicas de surto ou não. Essa classificação será feita por meio do uso de visão computacional onde um modelo será treinado utilizando sinais de EEG convertidos para imagen utilizando STFT (Short-Time-Fourier-Transform).

A entrada do modelo será os espectogramas das séries de EEG e a saída esperada é a classificação do modelo entre com ou sem epilepsia. A unidade de análise será o pixel, tendo em vista que estamos tratando com visão computacional, as classes escolhidas são duas, com epilepsia ou sem epilepsia. O público interessado e uso pretendido é cituado nos seguintes grupos: profissionais da área da saúde, pesquisadores, empresas que tem o objetivo de desenvolver tecnologias embarcadas para realizar essas detecções e também os pacientes com crises epilépticas.

O modelo deve ser avaliado utilizando métricas iniciais de sucesso, como a capacidade de discernir entre casos onde o paciente apresenta ou não a epilpesia, sendo a principal métrica a capacidade do modelo de atestar positivo em casos de crise e falso em casos que a crise não estiver presente.

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
