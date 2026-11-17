<template>
  <div class="trocar-senha-container">
    <form class="trocar-senha-card" novalidate @submit.prevent="salvar">
      <h1>Defina sua nova senha</h1>
      <p class="explicacao">
        Olá, {{ authStore.user?.nome }}. Por segurança, troque a senha provisória antes de usar o sistema.
      </p>

      <label for="senha-atual">Senha atual</label>
      <input id="senha-atual" v-model="senhaAtual" type="password" autocomplete="current-password" required :disabled="authStore.loading" />

      <label for="nova-senha">Nova senha</label>
      <input id="nova-senha" v-model="novaSenha" type="password" autocomplete="new-password" required :disabled="authStore.loading" aria-describedby="regras-senha" />

      <label for="confirmar-senha">Confirme a nova senha</label>
      <input id="confirmar-senha" v-model="confirmacao" type="password" autocomplete="new-password" required :disabled="authStore.loading" />

      <ul id="regras-senha" class="regras" aria-label="Regras da nova senha">
        <li v-for="regra in regras" :key="regra.texto" :class="{ ok: regra.ok }">
          <span aria-hidden="true">{{ regra.ok ? "✓" : "•" }}</span> {{ regra.texto }}
        </li>
      </ul>

      <p v-if="erro" class="erro" role="alert">{{ erro }}</p>

      <button type="submit" class="btn-salvar" :disabled="authStore.loading || !valida">
        {{ authStore.loading ? "Salvando..." : "Salvar nova senha" }}
      </button>
      <button type="button" class="btn-sair" :disabled="authStore.loading" @click="sair">Sair</button>
    </form>
  </div>
</template>

<script>
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { regrasSenha } from "@/utils/senha";

export default {
  name: "TrocarSenhaView",
  setup() {
    return { authStore: useAuthStore(), router: useRouter() };
  },
  data: () => ({ senhaAtual: "", novaSenha: "", confirmacao: "", erro: "" }),
  computed: {
    regras() { return regrasSenha(this.novaSenha, this.confirmacao, this.senhaAtual); },
    valida() { return Boolean(this.senhaAtual) && this.regras.every((regra) => regra.ok); },
  },
  methods: {
    async salvar() {
      this.erro = "";
      if (!this.valida) {
        this.erro = "Confira os campos e as regras da nova senha.";
        return;
      }
      const resultado = await this.authStore.trocarSenha(this.senhaAtual, this.novaSenha.trim());
      if (!resultado.success) {
        this.erro = resultado.message;
        return;
      }
      window.$modal?.abrir({ titulo: "Senha alterada", mensagem: "Sua senha foi alterada com sucesso.", tipo: "alerta" });
      this.router.push("/provas");
    },
    sair() {
      this.authStore.logout();
      this.router.push("/");
    },
  },
};
</script>

<style scoped>
.trocar-senha-container { position: fixed; inset: 0; min-height: 100dvh; display: flex; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; background: #00488b; overflow-y: auto; }
.trocar-senha-card { box-sizing: border-box; width: 100%; max-width: 420px; padding: 32px; background: white; color: #333; border-radius: 12px; box-shadow: 0 10px 30px #0003; display: flex; flex-direction: column; }
h1 { margin: 0 0 8px; font-size: 22px; color: #00488b; }
.explicacao { margin: 0 0 20px; font-size: 14px; line-height: 1.5; color: #555; }
label { margin: 12px 0 6px; font-size: 13px; font-weight: 600; }
input { padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 15px; }
input:focus { outline: 2px solid #00488b; outline-offset: 1px; }
.regras { list-style: none; margin: 16px 0 0; padding: 0; font-size: 13px; color: #777; }
.regras li { margin: 3px 0; }
.regras li.ok { color: #218838; }
.erro { margin: 14px 0 0; color: #b42318; font-size: 14px; }
.btn-salvar { margin-top: 20px; padding: 12px; border: 0; border-radius: 6px; background: #00488b; color: white; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-salvar:disabled { opacity: .5; cursor: not-allowed; }
.btn-sair { margin-top: 10px; padding: 10px; border: 0; background: transparent; color: #00488b; cursor: pointer; text-decoration: underline; }
@media (max-width: 480px) { .trocar-senha-card { padding: 24px 18px; } }
</style>
