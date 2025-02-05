function sendMessage() {
  let chatBox = document.getElementById("chat-box");
  let chatInput = document.getElementById("chat-input");

  if (chatInput.value.trim() !== "") {
    let message = document.createElement("p");
    message.innerText = "Instructor: " + chatInput.value;
    chatBox.appendChild(message);
    chatInput.value = "";

    // Auto-reply (Simulated)
    setTimeout(() => {
      let reply = document.createElement("p");
      reply.innerText = "Support: How can I assist you?";
      reply.style.color = "blue";
      chatBox.appendChild(reply);
    }, 1000);
  }
}
