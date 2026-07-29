import { createRoot } from 'react-dom/client';

import './lib/api'; // configure auth token + base URL for API client
import App from './App';

import './index.css';

createRoot(document.getElementById('root')!).render(<App />);
