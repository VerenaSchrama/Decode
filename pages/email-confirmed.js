import React from 'react';
import Head from 'next/head';

export default function EmailConfirmed() {
  React.useEffect(() => {
    // Auto-redirect after 3 seconds
    const timer = setTimeout(() => {
      window.location.href = '/';
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <Head>
        <title>Email Confirmed - HerFoodCode</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>
      <div style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        margin: 0,
        padding: '20px',
        backgroundColor: '#f8fafc',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '40px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
          maxWidth: '400px',
          width: '100%'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
          <h1 style={{ color: '#059669', marginBottom: '16px', fontSize: '24px' }}>
            Email Confirmed!
          </h1>
          <p style={{ color: '#6b7280', marginBottom: '24px', lineHeight: '1.5' }}>
            Your email has been successfully verified. You can now continue with your health journey.
          </p>
          
          <a href="/" style={{
            backgroundColor: '#059669',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            textDecoration: 'none',
            display: 'inline-block',
            margin: '8px'
          }}>
            Continue to App
          </a>
          <a href="/login" style={{
            backgroundColor: 'transparent',
            color: '#059669',
            border: '1px solid #059669',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            textDecoration: 'none',
            display: 'inline-block',
            margin: '8px'
          }}>
            Go to Login
          </a>
        </div>
      </div>
    </>
  );
}
