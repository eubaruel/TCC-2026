<template>
  <div class="informacoes-container">
    <div class="page-header">
      <h2>Informações</h2>
      <div class="header-line"></div>
    </div>
    <dl class="dados-usuario" aria-label="Dados do usuário">
      <div class="dado-usuario">
        <dt>Nome</dt>
        <dd>{{ authStore.user?.nome || 'Não informado' }}</dd>
      </div>
      <div class="dado-usuario">
        <dt>E-mail</dt>
        <dd>{{ authStore.user?.email || 'Não informado' }}</dd>
      </div>
      <div class="dado-usuario">
        <dt>Registro</dt>
        <dd>{{ authStore.user?.registro ?? 'Não informado' }}</dd>
      </div>
    </dl>
    <footer class="creditos" aria-label="Créditos do projeto">
      <p class="creditos-titulo">Desenvolvido por — 3°J · 2026</p>
      <ul>
        <li v-for="autor in autores" :key="autor.github">
          {{ autor.nome }} —
          <a :href="`https://github.com/${autor.github}`" target="_blank" rel="noopener noreferrer"
            :aria-label="`GitHub de ${autor.nome}`">@{{ autor.github }}</a>
        </li>
      </ul>
    </footer>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "InformacoesView",
  setup() {
    return { authStore: useAuthStore() };
  },
  data: () => ({
    autores: [
      { nome: "Jean Machado Brasil", github: "jeanmbr" },
      { nome: "Vitor Doring Leitão", github: "VitorDoring" },
      { nome: "Lucas Baruel Cestaro", github: "eubaruel" },
    ],
  }),
};
</script>

<style scoped>
.informacoes-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { margin: 20px 0 15px; font-size: 28px; font-weight: 600; color: inherit; }
.header-line { height: 2px; background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%); }
.dados-usuario { margin: 0; padding: 8px 24px; border: 1px solid #e0e0e0; border-radius: 12px; background: #fff; }
.dado-usuario { padding: 20px 0; }
.dado-usuario + .dado-usuario { border-top: 1px solid #e0e0e0; }
dt { margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #666; }
dd { margin: 0; font-size: 16px; line-height: 1.5; color: inherit; overflow-wrap: anywhere; }
:global(.tema-escuro .dados-usuario) { background: #2a2a2a; border-color: #404040; }
:global(.tema-escuro .dado-usuario + .dado-usuario) { border-color: #404040; }
:global(.tema-escuro .dado-usuario dt) { color: #b5b5b5; }
.creditos { margin: 32px 0 20px; padding-top: 16px; border-top: 1px solid #e0e0e0; text-align: center; font-size: 13px; color: #666; }
.creditos-titulo { margin: 0 0 8px; font-weight: 600; }
.creditos ul { list-style: none; margin: 0; padding: 0; }
.creditos li { margin: 4px 0; }
.creditos a { color: #00488b; font-weight: 600; text-decoration: none; border-bottom: 1px dashed transparent; transition: color .2s, border-color .2s; }
.creditos a:hover, .creditos a:focus-visible { color: #0066cc; border-bottom-color: currentColor; }
:global(.tema-escuro .creditos) { border-color: #404040; color: #b5b5b5; }
:global(.tema-escuro .creditos a) { color: #8ac4ff; }
@media (max-width: 480px) { .dados-usuario { padding: 4px 16px; } }
</style>
