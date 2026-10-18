const baseUrl = (process.env.VUE_APP_API_BASE_URL || "http://localhost:8080/api/v1").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export async function api(path, options = {}) {
  const headers = { Accept: "application/json", ...options.headers };
  const requestOptions = { ...options, headers };

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    requestOptions.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(`${baseUrl}${path}`, requestOptions);
  } catch (error) {
    throw new ApiError("Não foi possível conectar ao servidor.", 0, error.message);
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch (_) {
    throw new ApiError("O servidor retornou uma resposta inválida.", response.status);
  }

  if (!response.ok || !payload.sucesso) {
    const details = payload?.erro?.detalhes || payload?.erro?.mensagem || payload?.erro || null;
    throw new ApiError(payload?.mensagem || "Não foi possível concluir a operação.", response.status, details);
  }

  return payload.data;
}
