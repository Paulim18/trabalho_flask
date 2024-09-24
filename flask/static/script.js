document.addEventListener('DOMContentLoaded', function () {
    const addPerguntaButton = document.getElementById('add-pergunta');
    const perguntasContainer = document.getElementById('perguntas-container');

    let perguntaCount = 0;

    addPerguntaButton.addEventListener('click', function () {
        perguntaCount++;

        // Cria um novo contêiner para a pergunta
        const perguntaDiv = document.createElement('div');
        perguntaDiv.className = 'pergunta';

        perguntaDiv.innerHTML = `
            <label>Pergunta ${perguntaCount}:</label>
            <input type="text" name="pergunta_texto_${perguntaCount}" required>
            <select name="pergunta_tipo_${perguntaCount}" required>
                <option value="resposta_curta">Resposta Curta</option>
                <option value="resposta_longa">Resposta Longa</option>
                <option value="multipla_escolha">Múltipla Escolha</option>
                <option value="caixa_de_selecao">Caixa de Seleção</option>
            </select>
            <div class="alternativas-container"></div>
            <button type="button" class="add-alternativa">Adicionar Alternativa</button>
            <button type="button" class="remover-pergunta">Remover Pergunta</button>
        `;

        // Adiciona eventos aos botões de adicionar alternativa e remover pergunta
        const addAlternativaButton = perguntaDiv.querySelector('.add-alternativa');
        const removerPerguntaButton = perguntaDiv.querySelector('.remover-pergunta');

        addAlternativaButton.addEventListener('click', function () {
            const alternativasContainer = perguntaDiv.querySelector('.alternativas-container');
            const alternativaCount = alternativasContainer.childElementCount + 1;

            const alternativaDiv = document.createElement('div');
            alternativaDiv.innerHTML = `
                <input type="text" name="alternativa_texto_${perguntaCount}_${alternativaCount}" required>
                <button type="button" class="remover-alternativa">Remover Alternativa</button>
            `;
            alternativasContainer.appendChild(alternativaDiv);

            // Adiciona evento para remover a alternativa
            const removerAlternativaButton = alternativaDiv.querySelector('.remover-alternativa');
            removerAlternativaButton.addEventListener('click', function () {
                alternativasContainer.removeChild(alternativaDiv);
            });
        });

        // Adiciona o novo contêiner da pergunta ao contêiner principal
        perguntasContainer.appendChild(perguntaDiv);

        // Adiciona evento para remover a pergunta
        removerPerguntaButton.addEventListener('click', function () {
            perguntasContainer.removeChild(perguntaDiv);
        });
    });
});
