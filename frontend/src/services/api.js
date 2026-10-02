async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const error = await response.json();
      message = typeof error.detail === 'string' ? error.detail : message;
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  getTransactions: () => request('/transactions/?skip=0&limit=100'),
  getDisputes: () => request('/api/disputes'),
  getDispute: (disputeId) => request(`/api/disputes/${encodeURIComponent(disputeId)}`),
  resolveDispute: (payload) => request('/api/disputes/resolve', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  predictRisk: (payload) => request('/api/fraud/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  chatAssistant: (payload) => request('/api/assistant/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
};
