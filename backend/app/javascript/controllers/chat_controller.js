import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["window", "toggleBtn", "messages", "input", "sendBtn"]
  static values = { username: String }

  connect() {
    this.isOpen = false
  }

  toggle() {
    this.isOpen = !this.isOpen
    this.element.classList.toggle("open", this.isOpen)

    if (this.isOpen) {
      this.inputTarget.focus()
      this.scrollToBottom()
    }
  }

  async send(event) {
    event.preventDefault()

    const message = this.inputTarget.value.trim()
    if (!message) return

    // Clear input and disable while sending
    this.inputTarget.value = ""
    this.sendBtnTarget.disabled = true

    // Add user message to chat
    this.addMessage(message, "user")

    // Show typing indicator
    const typingIndicator = this.addTypingIndicator()

    try {
      const response = await fetch("http://localhost:5000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: this.usernameValue,
          query: message
        })
      })

      const data = await response.json()

      // Remove typing indicator
      typingIndicator.remove()

      if (data.error) {
        this.addMessage("Sorry, something went wrong. Please try again.", "assistant")
      } else {
        this.addMessage(data.result, "assistant")
      }
    } catch (error) {
      console.error("Chat error:", error)
      typingIndicator.remove()
      this.addMessage("Sorry, I couldn't connect to the server. Please try again.", "assistant")
    }

    this.sendBtnTarget.disabled = false
    this.inputTarget.focus()
  }

  addMessage(content, type) {
    const messageDiv = document.createElement("div")
    messageDiv.className = `chat-message ${type}`
    messageDiv.innerHTML = `<div class="message-content">${this.escapeHtml(content)}</div>`

    this.messagesTarget.appendChild(messageDiv)
    this.scrollToBottom()

    return messageDiv
  }

  addTypingIndicator() {
    const typingDiv = document.createElement("div")
    typingDiv.className = "chat-message assistant typing"
    typingDiv.innerHTML = `
      <div class="message-content">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `

    this.messagesTarget.appendChild(typingDiv)
    this.scrollToBottom()

    return typingDiv
  }

  scrollToBottom() {
    this.messagesTarget.scrollTop = this.messagesTarget.scrollHeight
  }

  escapeHtml(text) {
    const div = document.createElement("div")
    div.textContent = text
    return div.innerHTML
  }
}
