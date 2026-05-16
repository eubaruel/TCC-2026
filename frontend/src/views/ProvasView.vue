<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>Montar Prova</h2>
      <div class="header-line"></div>
    </div>
    
    <div class="provas-content">
      <div class="card-desenvolvimento">
        <div class="card-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8V12L15 15M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2 22 6.477 22 12 17.523 22 12 22Z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 6V12L15 15" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </div>
        <h3>Funcionalidade em Desenvolvimento</h3>
        <p>Em breve você poderá montar suas provas selecionando questões do banco de questões.</p>
        <p class="info-text">Aguardem novidades em breve!</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProvasView'
}
</script>

<style scoped>
.provas-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 15px;
  margin-top: 20px;
  color: inherit;
}

.header-line {
  height: 2px;
  background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%);
  width: 100%;
}

.provas-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.card-desenvolvimento {
  background: white;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  max-width: 500px;
  width: 100%;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tema-escuro .card-desenvolvimento {
  background: #2a2a2a;
  border-color: #404040;
}

.card-icon {
  margin-bottom: 24px;
  color: #00488b;
}

.tema-escuro .card-icon {
  color: #0066cc;
}

.card-desenvolvimento h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: inherit;
}

.card-desenvolvimento p {
  font-size: 16px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}

.tema-escuro .card-desenvolvimento p {
  color: #aaa;
}

.card-desenvolvimento .info-text {
  font-size: 14px;
  color: #888;
  margin-top: 16px;
}

.tema-escuro .card-desenvolvimento .info-text {
  color: #888;
}

@media (max-width: 768px) {
  .card-desenvolvimento {
    padding: 32px 24px;
  }
  
  .card-desenvolvimento h3 {
    font-size: 20px;
  }
  
  .card-desenvolvimento p {
    font-size: 14px;
  }
}
</style>