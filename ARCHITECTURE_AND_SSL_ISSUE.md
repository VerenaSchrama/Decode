# Architecture and SSL Issue Explanation

## Your Application Architecture

### Frontend (Web App)
- **Hosted on:** Vercel
- **Domain:** `https://decodev1.vercel.app`
- **IP:** Provided by Vercel (dynamic)
- **Status:** ✅ Working fine

### Backend (API Server)
- **Hosted on:** Hetzner server (65.108.149.135)
- **Domain:** `https://api.decode-app.nl` (TransIP DNS)
- **IP:** 65.108.149.135
- **Status:** ✅ Server working, ❌ SSL issue

## The Connection Flow

```
User's Browser
    ↓
Frontend (Vercel) - decodev1.vercel.app
    ↓ (API calls)
Backend API (TransIP domain) - api.decode-app.nl
    ↓ (DNS resolution)
TransIP DDoS Protection - blocked.transip.nl
    ↓ (filtered traffic)
Your Server - 65.108.149.135
```

## Why TransIP DDoS Protection Activated

### Yes, Because You Use TransIP for Backend Domain

**The relationship:**
1. **Backend domain** (`api.decode-app.nl`) is managed by **TransIP DNS**
2. **TransIP provides DNS services** for your domain
3. **TransIP also offers DDoS Protection** as an add-on service
4. **When protection activates**, it routes traffic through their infrastructure

### Not Because of Vercel

**Vercel is separate:**
- Vercel hosts your **frontend** (web app)
- Vercel has nothing to do with your **backend domain**
- The SSL issue is **only** with the backend API domain
- Frontend on Vercel works fine ✅

## Why This Matters

### The Problem Chain:

1. **Backend domain** (`api.decode-app.nl`) is registered/managed via **TransIP**
2. **TransIP DNS** points to your server (65.108.149.135)
3. **TransIP DDoS Protection** was activated (automatic or manual)
4. **Protection service** intercepts traffic to `api.decode-app.nl`
5. **Protection service** uses default SSL certificate (`*.vdx.nl`)
6. **Certificate mismatch** causes SSL errors

### The Frontend (Vercel) is Fine:

- Frontend on Vercel works perfectly
- Frontend makes API calls to `api.decode-app.nl`
- Those API calls fail because of SSL certificate issue
- But the frontend itself is not the problem

## Architecture Breakdown

### What's Where:

```
┌─────────────────────────────────────────┐
│  FRONTEND (Vercel)                      │
│  - decodev1.vercel.app                  │
│  - React Native Web App                 │
│  - Status: ✅ Working                   │
└─────────────────────────────────────────┘
              │
              │ API calls
              ↓
┌─────────────────────────────────────────┐
│  BACKEND DOMAIN (TransIP DNS)           │
│  - api.decode-app.nl                    │
│  - Managed by TransIP                   │
│  - Status: ❌ SSL Certificate Issue     │
└─────────────────────────────────────────┘
              │
              │ DNS resolution
              ↓
┌─────────────────────────────────────────┐
│  DDoS PROTECTION (TransIP)              │
│  - blocked.transip.nl                   │
│  - Intercepts HTTPS                     │
│  - Uses wrong certificate (*.vdx.nl)    │
│  - Status: ❌ Needs SSL configuration   │
└─────────────────────────────────────────┘
              │
              │ Filtered traffic
              ↓
┌─────────────────────────────────────────┐
│  BACKEND SERVER (Hetzner)               │
│  - 65.108.149.135                      │
│  - FastAPI application                 │
│  - Status: ✅ Working correctly         │
└─────────────────────────────────────────┘
```

## Why TransIP DDoS Protection Activated

### Possible Reasons:

1. **You're using TransIP DNS** for the backend domain
2. **TransIP offers DDoS Protection** as part of their services
3. **Automatic activation** based on traffic patterns
4. **Or manual activation** if you enabled it

### The Connection:

- **Backend domain** = TransIP DNS → DDoS Protection available
- **Frontend** = Vercel → Separate, not related to this issue

## The Fix

### What Needs to Happen:

1. **Configure SSL in TransIP DDoS Protection**
   - Upload your Let's Encrypt certificate
   - This fixes the SSL issue for `api.decode-app.nl`

2. **Or disable DDoS Protection**
   - Point DNS directly to your server
   - Your server's certificate will work

### What Doesn't Need to Change:

- ✅ Frontend on Vercel (working fine)
- ✅ Backend server (working fine)
- ✅ Backend code (working fine)
- ❌ Only the SSL certificate configuration in TransIP

## Summary

**Yes, the issue is because:**
- You use **TransIP for backend domain** (`api.decode-app.nl`)
- TransIP DDoS Protection was activated
- Protection service needs SSL certificate configuration

**No, it's not because:**
- Vercel (frontend is separate and working)
- Your server (server is working correctly)
- Your code (code is working correctly)

**The relationship:**
- **Backend domain** = TransIP → DDoS Protection activated
- **Frontend** = Vercel → Separate, not affected
- **Issue** = SSL certificate in TransIP DDoS Protection

