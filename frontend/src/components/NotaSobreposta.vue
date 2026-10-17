<template>
  <span class="nota-sobreposta" :style="posicaoNota(ajusteX, ajusteY)">{{ formatarNota(nota) }}</span>
</template>

<script>
import { formatarNota, posicaoNota } from "@/utils/impressaoNotas";

export default {
  name: "NotaSobreposta",
  props: { nota: { type: Number, required: true }, ajusteX: { type: Number, default: 0 }, ajusteY: { type: Number, default: 0 } },
  methods: { formatarNota, posicaoNota },
};
</script>

<style scoped>
.nota-sobreposta { position: absolute; transform: translate(-50%, -50%); display: flex; align-items: center; justify-content: center; box-sizing: border-box; white-space: nowrap; color: black; background: transparent; font: 400 12pt/1 Arial, sans-serif; }
</style>
