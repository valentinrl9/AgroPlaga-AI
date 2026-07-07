const form = document.getElementById("contact-form");
const msg = document.getElementById("form-msg");

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    msg.textContent = "Enviando…";
    msg.className = "form-msg";

    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      role: form.role.value,
      message: form.message.value.trim(),
    };

    try {
      const response = await fetch("/api/v1/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const detail = data.detail;
        const text = Array.isArray(detail)
          ? detail.map((item) => item.msg || item).join(" ")
          : detail || "No se pudo enviar el mensaje.";
        throw new Error(text);
      }

      form.reset();
      msg.textContent = "¡Gracias! Hemos recibido tu mensaje. Te contactaremos pronto.";
      msg.className = "form-msg ok";
    } catch (error) {
      msg.textContent = error.message || "Error de conexión. Inténtalo más tarde.";
      msg.className = "form-msg err";
    }
  });
}
