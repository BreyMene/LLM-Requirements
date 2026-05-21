import { useMemo, useState } from 'react';

const modes = [
  {
    key: 'analyze',
    title: 'Analizar requisito',
    subtitle: 'Audita un requisito para calidad, claridad y formato Gherkin.',
    label: 'Requisito a analizar',
    button: 'Analizar',
    fieldName: 'text',
    outputKey: 'analysis',
    placeholder: 'Escribe aquí un requisito, por ejemplo: El sistema debe autenticar usuarios con OAuth 2.0.'
  },
  {
    key: 'generate',
    title: 'Generar requisitos',
    subtitle: 'Crea requisitos funcionales y no funcionales desde una descripción.',
    label: 'Descripción del producto',
    button: 'Generar',
    fieldName: 'description',
    outputKey: 'requirements',
    placeholder: 'Describe la solución que necesitas, por ejemplo: un sistema de reservas que permita pagos y notificaciones.'
  }
];

function App() {
  const [activeMode, setActiveMode] = useState(modes[0].key);
  const [inputText, setInputText] = useState('');
  const [resultText, setResultText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const mode = useMemo(() => modes.find((item) => item.key === activeMode), [activeMode]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!inputText.trim()) {
      setError('Por favor escribe un texto válido antes de continuar.');
      return;
    }

    setLoading(true);
    setError('');
    setResultText('');

    try {
      const response = await fetch(`/${activeMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [mode.fieldName]: inputText.trim() })
      });

      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.detail || 'Error al comunicarse con el backend.');
      }

      const data = await response.json();
      setResultText(data[mode.outputKey] || 'No se recibió respuesta del servidor.');
    } catch (err) {
      setError(err.message || 'Ocurrió un error inesperado.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setInputText('');
    setResultText('');
    setError('');
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span>LLM</span>
          <h1>Requisitos AI</h1>
        </div>

        <div className="nav-group">
          <h2>Modos Generativos</h2>
          {modes.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`nav-item ${item.key === activeMode ? 'active' : ''}`}
              onClick={() => {
                setActiveMode(item.key);
                setResultText('');
                setError('');
              }}
            >
              <span>{item.title}</span>
              <small>{item.subtitle}</small>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <p>Responsive + moderno. Ejecuta el backend en <strong>localhost:8000</strong>.</p>
        </div>
      </aside>

      <main className="content">
        <section className="hero-card">
          <div>
            <p className="eyebrow">Dashboard de generación</p>
            <h2>{mode.title}</h2>
            <p>{mode.subtitle}</p>
          </div>
          <div className="hero-meta">
            <span>{loading ? 'Generando...' : 'Listo para usar'}</span>
          </div>
        </section>

        <form className="form-card" onSubmit={handleSubmit}>
          <label htmlFor="inputText">{mode.label}</label>
          <textarea
            id="inputText"
            value={inputText}
            rows={8}
            placeholder={mode.placeholder}
            onChange={(event) => setInputText(event.target.value)}
          />

          <div className="actions">
            <button type="submit" disabled={loading} className="primary-button">
              {loading ? 'Procesando...' : mode.button}
            </button>
            <button type="button" className="secondary-button" onClick={handleReset}>
              Limpiar
            </button>
          </div>

          {error && <div className="alert error">{error}</div>}

          {resultText && (
            <div className="result-panel">
              <div className="result-header">
                <h3>Resultado</h3>
                <span>{mode.title}</span>
              </div>
              <pre>{resultText}</pre>
            </div>
          )}
        </form>
      </main>
    </div>
  );
}

export default App;
