// Mesmas regras de backend/api/modelos/usuario.py.
const ESPECIAIS = "!@#$%^&*(),.?\":{}|<>";

export function regrasSenha(senha, confirmacao, senhaAtual) {
  const valor = (senha || "").trim();
  return [
    { texto: "Ao menos 6 caracteres", ok: valor.length >= 6 },
    { texto: "Uma letra maiúscula", ok: /[A-ZÀ-Ý]/.test(valor) },
    { texto: "Um número", ok: /\d/.test(valor) },
    { texto: `Um caractere especial (${ESPECIAIS})`, ok: [...valor].some((c) => ESPECIAIS.includes(c)) },
    { texto: "Diferente da senha atual", ok: Boolean(valor) && valor !== (senhaAtual || "").trim() },
    { texto: "Confirmação igual à nova senha", ok: Boolean(valor) && senha === confirmacao },
  ];
}
