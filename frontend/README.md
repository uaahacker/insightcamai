# Frontend - CCTV Analytics SaaS

React + TypeScript frontend for the CCTV Analytics platform.

## Development

```bash
npm install
npm run dev
```

The frontend will run on http://localhost:5173

## Build

```bash
npm run build
```

## Environment Variables

Create a `.env.local` file:

```
VITE_API_URL=http://localhost:8000/api/v1
```

## Project Structure

- `src/pages/` - Page components
- `src/components/` - Reusable components
- `src/api/` - API client and endpoints
- `src/store/` - Zustand state management
- `src/types/` - TypeScript type definitions
