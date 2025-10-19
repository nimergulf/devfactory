# DevFoundry Frontend & CLI Packages

## Complete Frontend Technology Stack

This document covers the JavaScript/TypeScript packages for DevFoundry Studio (web console) and DevFoundry CLI.

---

## 📦 Package Structure

```
devfoundry/
├── apps/
│   ├── studio/          # Web console (Next.js)
│   └── cli/             # CLI tool (Node.js)
├── packages/
│   ├── ui/              # Shared UI components
│   ├── api-client/      # API SDK
│   └── shared/          # Shared utilities
└── package.json         # Root workspace config
```

---

## 🎨 DevFoundry Studio (Web Console)

### Core Framework: **Next.js 14**

**package.json (apps/studio)**:
```json
{
  "name": "@devfoundry/studio",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    
    "tailwindcss": "3.3.5",
    "@tailwindcss/typography": "0.5.10",
    "@tailwindcss/forms": "0.5.7",
    
    "shadcn-ui": "latest",
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-dropdown-menu": "2.0.6",
    "@radix-ui/react-select": "2.0.0",
    "@radix-ui/react-tabs": "1.0.4",
    "@radix-ui/react-toast": "1.1.5",
    "@radix-ui/react-tooltip": "1.0.7",
    
    "lucide-react": "0.294.0",
    "class-variance-authority": "0.7.0",
    "clsx": "2.0.0",
    "tailwind-merge": "2.1.0",
    
    "zustand": "4.4.7",
    "react-query": "3.39.3",
    "@tanstack/react-query": "5.8.4",
    
    "axios": "1.6.2",
    "socket.io-client": "4.6.0",
    
    "@monaco-editor/react": "4.6.0",
    "react-markdown": "9.0.1",
    "remark-gfm": "4.0.0",
    "rehype-highlight": "7.0.0",
    
    "recharts": "2.10.3",
    "react-flow-renderer": "10.3.17",
    "mermaid": "10.6.1",
    
    "date-fns": "2.30.0",
    "zod": "3.22.4",
    "react-hook-form": "7.48.2",
    "@hookform/resolvers": "3.3.2",
    
    "next-themes": "0.2.1",
    "next-auth": "4.24.5",
    
    "framer-motion": "10.16.16"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.42",
    "@types/react-dom": "18.2.17",
    "typescript": "5.3.2",
    "eslint": "8.54.0",
    "eslint-config-next": "14.0.3",
    "@typescript-eslint/eslint-plugin": "6.13.1",
    "@typescript-eslint/parser": "6.13.1",
    "prettier": "3.1.0",
    "prettier-plugin-tailwindcss": "0.5.7",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.31"
  }
}
```

### Why Next.js 14?

**Benefits**:
- ✅ **Server Components**: Reduced client bundle size
- ✅ **App Router**: Modern routing with layouts
- ✅ **API Routes**: Backend API in same codebase
- ✅ **SSR/SSG**: Better SEO and performance
- ✅ **Image Optimization**: Automatic image optimization
- ✅ **TypeScript**: First-class TypeScript support

### UI Library: **shadcn/ui + Radix UI**

**Why shadcn/ui?**
- ✅ **Copy-paste components**: Own your code, no node_modules bloat
- ✅ **Radix primitives**: Accessible, unstyled components
- ✅ **TailwindCSS**: Utility-first styling
- ✅ **Customizable**: Full control over design
- ✅ **Modern**: Uses latest React patterns

**Component Example**:
```tsx
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader } from "@/components/ui/dialog"
import { toast } from "@/components/ui/use-toast"

export function WorkflowDialog({ workflowId }: { workflowId: string }) {
  return (
    <Dialog>
      <DialogContent>
        <DialogHeader>
          <h2>Workflow Progress</h2>
        </DialogHeader>
        <WorkflowProgress id={workflowId} />
        <Button onClick={() => toast({ title: "Workflow started" })}>
          Start Workflow
        </Button>
      </DialogContent>
    </Dialog>
  )
}
```

### State Management: **Zustand**

**Why Zustand over Redux?**
- ✅ **Simple API**: Less boilerplate
- ✅ **TypeScript**: Excellent TS support
- ✅ **Small bundle**: 1KB gzipped
- ✅ **No Context**: No provider hell
- ✅ **Middleware**: Built-in persist, devtools

**Store Example**:
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface WorkflowStore {
  workflows: Workflow[]
  activeWorkflow: string | null
  setActiveWorkflow: (id: string) => void
  addWorkflow: (workflow: Workflow) => void
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void
}

export const useWorkflowStore = create<WorkflowStore>()(
  persist(
    (set) => ({
      workflows: [],
      activeWorkflow: null,
      setActiveWorkflow: (id) => set({ activeWorkflow: id }),
      addWorkflow: (workflow) => 
        set((state) => ({ workflows: [...state.workflows, workflow] })),
      updateWorkflow: (id, updates) =>
        set((state) => ({
          workflows: state.workflows.map((w) =>
            w.id === id ? { ...w, ...updates } : w
          ),
        })),
    }),
    { name: 'workflow-storage' }
  )
)
```

### Data Fetching: **TanStack Query (React Query)**

**Why React Query?**
- ✅ **Caching**: Automatic request deduplication
- ✅ **Background refetch**: Keep data fresh
- ✅ **Optimistic updates**: Better UX
- ✅ **DevTools**: Debugging made easy
- ✅ **TypeScript**: Full type safety

**Query Example**:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Fetch workflow
export function useWorkflow(workflowId: string) {
  return useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => api.getWorkflow(workflowId),
    refetchInterval: 5000, // Poll every 5s
  })
}

// Create workflow
export function useCreateWorkflow() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: CreateWorkflowInput) => api.createWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      toast({ title: 'Workflow created!' })
    },
  })
}

// Usage in component
function WorkflowList() {
  const { data: workflow, isLoading } = useWorkflow('wf-123')
  const createWorkflow = useCreateWorkflow()
  
  if (isLoading) return <Skeleton />
  
  return (
    <div>
      <WorkflowCard workflow={workflow} />
      <Button onClick={() => createWorkflow.mutate({ concept: '...' })}>
        Create New
      </Button>
    </div>
  )
}
```

### Real-time Updates: **Socket.io**

**WebSocket Integration**:
```typescript
import { io } from 'socket.io-client'
import { useEffect } from 'react'

const socket = io(process.env.NEXT_PUBLIC_API_URL!)

export function useWorkflowUpdates(workflowId: string) {
  const queryClient = useQueryClient()
  
  useEffect(() => {
    socket.emit('subscribe', { workflow_id: workflowId })
    
    socket.on('workflow:update', (data) => {
      queryClient.setQueryData(['workflow', workflowId], data)
    })
    
    socket.on('agent:completed', (data) => {
      toast({ title: `${data.agent} completed!` })
    })
    
    return () => {
      socket.emit('unsubscribe', { workflow_id: workflowId })
    }
  }, [workflowId])
}
```

### Code Editor: **Monaco Editor**

**Why Monaco?**
- ✅ **VS Code power**: Same editor as VS Code
- ✅ **IntelliSense**: Auto-completion
- ✅ **Multi-language**: 50+ languages
- ✅ **Diff viewer**: Compare code versions

**Editor Component**:
```tsx
import Editor from '@monaco-editor/react'

export function CodeViewer({ code, language }: CodeViewerProps) {
  return (
    <Editor
      height="600px"
      language={language}
      value={code}
      theme="vs-dark"
      options={{
        readOnly: true,
        minimap: { enabled: true },
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: true,
        scrollBeyondLastLine: false,
        automaticLayout: true,
      }}
    />
  )
}
```

### Visualization: **React Flow + Recharts**

**Workflow Visualization**:
```tsx
import ReactFlow, { Background, Controls } from 'react-flow-renderer'

const nodes = [
  { id: '1', data: { label: 'Product Agent' }, position: { x: 0, y: 0 } },
  { id: '2', data: { label: 'Architect Agent' }, position: { x: 0, y: 100 } },
]

const edges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
]

export function WorkflowGraph() {
  return (
    <ReactFlow nodes={nodes} edges={edges}>
      <Background />
      <Controls />
    </ReactFlow>
  )
}
```

**Metrics Dashboard**:
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export function MetricsChart({ data }: MetricsChartProps) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="latency" stroke="#8884d8" />
      <Line type="monotone" dataKey="throughput" stroke="#82ca9d" />
    </LineChart>
  )
}
```

---

## 🖥️ DevFoundry CLI

### Core: **Node.js + TypeScript**

**package.json (apps/cli)**:
```json
{
  "name": "@devfoundry/cli",
  "version": "1.0.0",
  "description": "DevFoundry command-line interface",
  "bin": {
    "devfoundry": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc && chmod +x dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest"
  },
  "dependencies": {
    "commander": "11.1.0",
    "inquirer": "9.2.12",
    "chalk": "5.3.0",
    "ora": "7.0.1",
    "cli-table3": "0.6.3",
    "boxen": "7.1.1",
    "update-notifier": "6.0.2",
    
    "axios": "1.6.2",
    "ws": "8.14.2",
    
    "conf": "12.0.0",
    "keytar": "7.9.0",
    
    "dotenv": "16.3.1",
    "zod": "3.22.4",
    
    "cosmiconfig": "9.0.0",
    "find-up": "7.0.0",
    
    "execa": "8.0.1",
    "globby": "14.0.0",
    
    "fs-extra": "11.2.0",
    "chokidar": "3.5.3",
    
    "listr2": "7.0.2",
    "p-queue": "8.0.1"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/inquirer": "9.0.7",
    "@types/fs-extra": "11.0.4",
    "typescript": "5.3.2",
    "ts-node": "10.9.1",
    "jest": "29.7.0",
    "ts-jest": "29.1.1",
    "@types/jest": "29.5.10"
  }
}
```

### CLI Framework: **Commander.js**

**Why Commander?**
- ✅ **Mature**: Industry standard
- ✅ **Flexible**: Subcommands, options, arguments
- ✅ **Auto-help**: Generated help text
- ✅ **TypeScript**: Full type support

**CLI Structure**:
```typescript
import { Command } from 'commander'
import chalk from 'chalk'
import ora from 'ora'

const program = new Command()

program
  .name('devfoundry')
  .description('DevFoundry CLI - Transform ideas into production code')
  .version('1.0.0')

program
  .command('init <project-name>')
  .description('Initialize a new DevFoundry project')
  .option('-a, --architecture <type>', 'Architecture style', 'microservice')
  .option('-d, --deployment <target>', 'Deployment target', 'cloud-run')
  .action(async (projectName, options) => {
    const spinner = ora('Initializing project...').start()
    
    try {
      await initProject(projectName, options)
      spinner.succeed(chalk.green('Project initialized!'))
    } catch (error) {
      spinner.fail(chalk.red('Initialization failed'))
      console.error(error)
    }
  })

program
  .command('generate')
  .description('Generate a complete solution from requirements')
  .option('-r, --requirement <text>', 'Requirement description')
  .option('-f, --file <path>', 'Load requirements from file')
  .option('--watch', 'Watch for changes and update')
  .action(async (options) => {
    const requirement = options.requirement || await readFromFile(options.file)
    
    const spinner = ora('Starting generation workflow...').start()
    
    const workflowId = await api.createWorkflow({ concept: requirement })
    spinner.text = `Workflow started: ${workflowId}`
    
    // Stream updates
    await streamWorkflowProgress(workflowId, spinner)
  })

program
  .command('status [workflow-id]')
  .description('Check workflow status')
  .action(async (workflowId) => {
    const status = await api.getWorkflowStatus(workflowId)
    displayWorkflowStatus(status)
  })

program.parse(process.argv)
```

### Interactive Prompts: **Inquirer**

**User Input**:
```typescript
import inquirer from 'inquirer'

async function promptForConfig() {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'projectName',
      message: 'Project name:',
      validate: (input) => input.length > 0,
    },
    {
      type: 'list',
      name: 'architecture',
      message: 'Choose architecture:',
      choices: ['Microservice', 'Monolith', 'Serverless', 'Event-Driven'],
    },
    {
      type: 'checkbox',
      name: 'compliance',
      message: 'Select compliance frameworks:',
      choices: ['ISO 27001', 'SOC 2', 'HIPAA', 'PCI DSS'],
    },
    {
      type: 'confirm',
      name: 'includeTests',
      message: 'Include test generation?',
      default: true,
    },
  ])
  
  return answers
}
```

### Progress Display: **Ora + Listr2**

**Task Lists**:
```typescript
import { Listr } from 'listr2'

const tasks = new Listr([
  {
    title: 'Analyzing requirements',
    task: async (ctx, task) => {
      ctx.requirements = await analyzeRequirements()
      task.title = `Requirements analyzed: ${ctx.requirements.features.length} features`
    },
  },
  {
    title: 'Generating architecture',
    task: async (ctx, task) => {
      ctx.architecture = await generateArchitecture(ctx.requirements)
      return task.newListr([
        {
          title: 'Creating ADRs',
          task: async () => await createADRs(ctx.architecture),
        },
        {
          title: 'Designing API',
          task: async () => await designAPI(ctx.architecture),
        },
      ])
    },
  },
  {
    title: 'Generating code',
    task: async (ctx) => {
      ctx.code = await generateCode(ctx.architecture)
    },
  },
])

await tasks.run()
```

### Configuration Management: **Conf**

**Persistent Config**:
```typescript
import Conf from 'conf'

const config = new Conf({
  projectName: 'devfoundry',
  defaults: {
    apiUrl: 'https://api.devfoundry.com',
    region: 'us-central1',
    outputFormat: 'json',
  },
})

// Get/set config
config.set('apiKey', 'sk-...')
const apiKey = config.get('apiKey')

// Secure storage for credentials
import keytar from 'keytar'
await keytar.setPassword('devfoundry', 'api-token', token)
const token = await keytar.getPassword('devfoundry', 'api-token')
```

---

## 📦 Shared Packages

### API Client

**packages/api-client/package.json**:
```json
{
  "name": "@devfoundry/api-client",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "dependencies": {
    "axios": "1.6.2",
    "zod": "3.22.4",
    "eventemitter3": "5.0.1"
  }
}
```

**SDK Implementation**:
```typescript
import axios, { AxiosInstance } from 'axios'
import { z } from 'zod'

const WorkflowSchema = z.object({
  id: z.string(),
  status: z.enum(['pending', 'in_progress', 'completed', 'failed']),
  created_at: z.string(),
  agents_completed: z.array(z.string()),
})

export class DevFoundryClient {
  private client: AxiosInstance
  
  constructor(apiUrl: string, apiKey: string) {
    this.client = axios.create({
      baseURL: apiUrl,
      headers: { Authorization: `Bearer ${apiKey}` },
    })
  }
  
  async createWorkflow(data: CreateWorkflowInput): Promise<Workflow> {
    const response = await this.client.post('/v1/workflows', data)
    return WorkflowSchema.parse(response.data)
  }
  
  async getWorkflow(id: string): Promise<Workflow> {
    const response = await this.client.get(`/v1/workflows/${id}`)
    return WorkflowSchema.parse(response.data)
  }
  
  streamWorkflow(id: string, onUpdate: (data: any) => void) {
    const ws = new WebSocket(`${this.wsUrl}/v1/workflows/${id}/stream`)
    ws.onmessage = (event) => onUpdate(JSON.parse(event.data))
    return () => ws.close()
  }
}
```

---

## 🎯 Development Tools

### Monorepo Management: **Turborepo**

**Why Turborepo?**
- ✅ **Fast builds**: Intelligent caching
- ✅ **Parallel execution**: Run tasks in parallel
- ✅ **Remote caching**: Share cache across team
- ✅ **Dependency graph**: Optimal task scheduling

**turbo.json**:
```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false
    }
  }
}
```

### Code Quality

**ESLint + Prettier**:
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

---

## 📊 Package Summary

### Frontend (Studio)
- **Framework**: Next.js 14
- **UI**: shadcn/ui + Radix UI + TailwindCSS
- **State**: Zustand
- **Data**: TanStack Query
- **Icons**: Lucide React
- **Editor**: Monaco Editor
- **Charts**: Recharts
- **Diagrams**: React Flow

### CLI
- **Framework**: Commander.js
- **Prompts**: Inquirer
- **Styling**: Chalk + Ora
- **Config**: Conf + Keytar
- **Tasks**: Listr2

### Shared
- **API**: Axios + Zod
- **Build**: Turborepo
- **TypeScript**: 5.3+
- **Testing**: Jest + React Testing Library

---

**Total Frontend Packages**: ~50  
**Bundle Size (Studio)**: ~200KB gzipped  
**CLI Binary Size**: ~15MB

---

**Document Version**: 1.0  
**Last Updated**: October 2024  
**Maintained By**: DevFoundry Frontend Team
