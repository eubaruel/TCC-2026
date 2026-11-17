<template>
  <!-- Fica fora do cartão-resposta: o interior do cartão é lido pelo corretor. -->
  <section v-if="conteudoLimpo || observacaoLimpa" class="informacoes-prova" aria-label="Informações da prova">
    <p v-if="conteudoLimpo"><strong>Conteúdo:</strong> {{ conteudoLimpo }}</p>
    <p v-if="observacaoLimpa"><strong>Observação:</strong> {{ observacaoLimpa }}</p>
  </section>
</template>

<script>
export default {
  name: "InformacoesProva",
  props: {
    conteudo: { type: String, default: "" },
    observacao: { type: String, default: "" },
  },
  computed: {
    conteudoLimpo() { return (this.conteudo || "").trim(); },
    observacaoLimpa() { return (this.observacao || "").trim(); },
  },
};
</script>

<style scoped>
.informacoes-prova {
  margin: 6px 0 0;
  padding: 4px 8px;
  border: 1px solid #000;
  color: #000;
  background: white;
  font-family: Arial, sans-serif;
  font-size: 9pt;
  line-height: 1.25;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  break-inside: avoid;
}

.informacoes-prova p {
  margin: 0;
}

.informacoes-prova p + p {
  margin-top: 2px;
}
</style>
