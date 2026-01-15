import React from 'react';

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in child component tree
 * and displays a fallback UI instead of crashing
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: 'var(--bg-main, #0a0a0f)',
          color: 'var(--text-primary, #ffffff)',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{
            backgroundColor: 'var(--bg-card, #12121a)',
            borderRadius: '12px',
            padding: '2rem',
            maxWidth: '600px',
            border: '1px solid rgba(255, 100, 100, 0.3)'
          }}>
            <h1 style={{ 
              color: 'var(--danger, #ff4444)', 
              marginBottom: '1rem',
              fontSize: '1.5rem'
            }}>
              ⚠️ Something went wrong
            </h1>
            
            <p style={{ 
              color: 'var(--text-muted, #888)', 
              marginBottom: '1.5rem' 
            }}>
              An unexpected error occurred in the application.
            </p>

            {this.state.error && (
              <details style={{ 
                textAlign: 'left', 
                marginBottom: '1.5rem',
                backgroundColor: 'rgba(0,0,0,0.3)',
                padding: '1rem',
                borderRadius: '8px',
                fontSize: '0.85rem'
              }}>
                <summary style={{ cursor: 'pointer', marginBottom: '0.5rem' }}>
                  Error Details
                </summary>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-word',
                  color: 'var(--danger, #ff4444)'
                }}>
                  {this.state.error.toString()}
                </pre>
                {this.state.errorInfo && (
                  <pre style={{ 
                    whiteSpace: 'pre-wrap', 
                    wordBreak: 'break-word',
                    color: 'var(--text-muted, #888)',
                    marginTop: '0.5rem',
                    fontSize: '0.75rem'
                  }}>
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </details>
            )}

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button
                onClick={this.handleReset}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'var(--primary, #00f2ff)',
                  color: '#000',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Try Again
              </button>
              <button
                onClick={this.handleReload}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: 'var(--text-primary, #fff)',
                  border: '1px solid var(--glass-border, rgba(255,255,255,0.1))',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
