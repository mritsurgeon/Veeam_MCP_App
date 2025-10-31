# Veeam MCP Chat Client - Frontend

React-based frontend for the Veeam MCP Chat Client, built with TypeScript, Tailwind CSS, and modern UI components.

## Features

- **Modern Chat Interface**: Clean, intuitive chat UI with message bubbles
- **Model Selection**: Switch between different LLM providers (OpenAI, Anthropic, Ollama)
- **Streaming Responses**: Real-time message streaming with SSE support
- **Artifact Rendering**: View generated dashboards, reports, and diagrams
- **Recent Chats**: Quick access to chat history
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Adapts to different screen sizes

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **React Markdown** for rendering markdown content
- **Axios** for API communication

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components (Button, Input, etc.)
│   │   ├── Sidebar.tsx   # Left sidebar with navigation and recent chats
│   │   ├── Header.tsx    # Top header with model selector
│   │   ├── ChatInterface.tsx  # Main chat interface
│   │   ├── ChatMessage.tsx    # Individual message component
│   │   └── ArtifactViewer.tsx # Artifact preview panel
│   ├── services/
│   │   └── api.ts        # API client for backend communication
│   ├── types/
│   │   └── index.ts      # TypeScript type definitions
│   ├── lib/
│   │   └── utils.ts      # Utility functions
│   ├── App.tsx           # Main application component
│   └── main.tsx          # Application entry point
├── public/               # Static assets
└── package.json
```

## Components

### Sidebar
- Displays navigation (Chats, Tools, Starred)
- Shows recent chat history
- "Start new chat" button

### Header
- Application title and branding
- Model selector dropdown
- Settings, dark mode, and refresh buttons

### ChatInterface
- Message list with user and assistant bubbles
- Input field with send button
- Support for streaming responses
- Tool output section

### ChatMessage
- Renders user and assistant messages
- Markdown support for assistant responses
- Timestamps and avatars
- Action buttons for artifacts

### ArtifactViewer
- Preview generated artifacts (dashboards, reports)
- Tabs for Preview and Code views
- Export functionality
- Close/maximize controls

## API Integration

The frontend communicates with the backend via the `/api/v1` endpoints:

- `POST /api/v1/chat` - Send chat messages
- `GET /api/v1/providers` - List available LLM providers
- `GET /api/v1/providers/{provider}/health` - Check provider health

## Styling

The app uses Tailwind CSS with a custom theme:
- **Primary Color**: Veeam green (`#10B981`)
- **Light Theme**: White background with gray accents
- **Dark Theme**: Dark background (toggleable)

## Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

## Development Tips

1. **Hot Module Replacement**: Vite provides instant updates during development
2. **TypeScript**: All components are fully typed for better development experience
3. **Tailwind IntelliSense**: Install the Tailwind CSS IntelliSense extension for autocomplete

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Mermaid diagram rendering
- [ ] Export artifacts to PDF/HTML
- [ ] Drag and drop file uploads
- [ ] Keyboard shortcuts
- [ ] Search functionality
- [ ] Chat export/import

