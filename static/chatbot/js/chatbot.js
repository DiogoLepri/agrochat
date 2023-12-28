
  const messagesList = document.querySelector('.messages-list');
  const messageForm = document.querySelector('.message-form');
  const messageInput = document.querySelector('.message-input');
  const messagesBox = document.querySelector('.messages-box');
  const btnScrollBottom = document.getElementById('btn-scroll-bottom'); // Corrected ID
    

  function updateUserInfo(username) {
    document.getElementById('user-username').innerText = username;
}


  function formatResponse(response) {
    const lines = response.split(/[:]/);
    const formattedResponse = lines.map(line => line.trim()).join(':\n');
    return formattedResponse;
  }


  function scrollToBottom() {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  messagesBox.addEventListener("scroll", function() {
    // Calculate the difference between the total height and the combined scroll position and viewport height
    let distanceFromBottom = messagesBox.scrollHeight - messagesBox.scrollTop - messagesBox.clientHeight;

    if (distanceFromBottom > 50) {
      btnScrollBottom.style.display = "block"; // Show the button
    } else {
      btnScrollBottom.style.display = "none"; // Hide the button
    }
  });

  btnScrollBottom.addEventListener('click', function() {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  });


  messageForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (message.length === 0) {
        return;
    }

    
    const messageItem = document.createElement('li');
    messageItem.classList.add('message', 'sent');
    messageItem.innerHTML = `
        <div class="message-text">
            <div class="message-sender">
                ${userUsername}
            </div>
            <div class="message-content">
            <br>
                ${message}
            </div>
        </div>`;
    messagesList.appendChild(messageItem);
    scrollToBottom();

    socket.send(JSON.stringify({
        message: message
    }));

    messageInput.value = '';

    fetch('', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'message': message
          })
        })
          .then(response => response.json())
          .then(data => {
            const response = formatResponse(data.response);
            const responseItem = document.createElement('li');
            responseItem.classList.add('message', 'received');
            responseItem.innerHTML = `
            <div class="message-text">
                <div class="message-sender">
                  <img id=lgg src="/static/images/logo.png"> <b>AgroChat</b>
                </div>
                <div class="message-content response">
                <br>
                    ${response}
                </div>
            </div>
              `;
            messagesList.appendChild(responseItem);
            scrollToBottom();
      });
  });

function askQuestion() {
    const question = "Qual é a sua pergunta?"; // Modifique para a pergunta desejada

    const messageItem = document.createElement('li');
    messageItem.classList.add('message', 'sent');
    messageItem.innerHTML = `
        <div class="message-text">
            <div class="message-sender">
                ${userUsername}
            </div>
            <div class="message-content">
            <br>
                ${question}
            </div>
        </div>`;
    messagesList.appendChild(messageItem);
    scrollToBottom();

    // Enviar a pergunta para o backend e obter a resposta
    fetch('', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'message': question
        })
    })
        .then(response => response.json())
        .then(data => {
            const response = data.response;
            const messageItem = document.createElement('li');
            messageItem.classList.add('message', 'received');
            messageItem.innerHTML = `
            <div class="message-text">
                <div class="message-sender">
                <img id=lgg src="/static/images/logo.png"> <b>AgroChat</b>
                </div>
                <div class="message-content">
                <br>
                    ${response}
                </div>
            </div>
            `;
            messagesList.appendChild(messageItem);
            scrollToBottom();
        });
}



    const btnAskQuestion1 = document.getElementById('btnAskQuestion1');
    const btnAskQuestion2 = document.getElementById('btnAskQuestion2');
    const btnAskQuestion3 = document.getElementById('btnAskQuestion3');
    const btnAskQuestion4 = document.getElementById('btnAskQuestion4');
    const btnAskQuestion6 = document.getElementById('btnAskQuestion6');

    function sendPredefinedQuestion(question) {
        sendMessageToChatbot(question);
    }

    btnAskQuestion1.addEventListener('click', function() {
        sendPredefinedQuestion("O que é o AgroChat?");
    });

    btnAskQuestion2.addEventListener('click', function() {
        sendPredefinedQuestion("Me de um exemplo de como fazer uma pergunta");
    });

    btnAskQuestion3.addEventListener('click', function() {
        sendPredefinedQuestion("Depois de amanha, qual sera o clima em londrina?");
    });

    btnAskQuestion4.addEventListener('click', function() {
        sendPredefinedQuestion("O que é o Intech Experience?");
    });


    btnAskQuestion6.addEventListener('click', function() {
        sendPredefinedQuestion("Atualmente, qual é o clima em Londrina?");
    });

    function sendMessageToChatbot(message) {
        const messageItem = document.createElement('li');
        messageItem.classList.add('message', 'sent');
        messageItem.innerHTML = `
            <div class="message-text">
                <div class="message-sender">
                    ${userUsername}
                </div>
                <div class="message-content">
                <br>
                    ${message}
                </div>
            </div>`;
        messagesList.appendChild(messageItem);

        fetch('', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'message': message
          })
        })
          .then(response => response.json())
          .then(data => {
            const response = formatResponse(data.response);
            const responseItem = document.createElement('li');
            responseItem.classList.add('message', 'received');
            responseItem.innerHTML = `
            <div class="message-text">
                <div class="message-sender">
                  <img id=lgg src="/static/images/logo.png"> <b>AgroChat</b>
                </div>
                <div class="message-content response">
                <br>
                    ${response}
                </div>
            </div>
              `;
            messagesList.appendChild(responseItem);
            scrollToBottom();
          });
    };