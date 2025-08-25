"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Loader2,
  Send,
  Code,
  Bot,
  User,
  Cpu,
  FolderTree,
  Rocket,
  FileText,
  Play,
  Download,
  Save,
  RefreshCw,
  Terminal,
  Package,
  Database,
  Globe,
  Paperclip,
  ImageIcon,
  FileArchive,
  X,
} from "lucide-react"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
  metadata?: any
  files?: UploadedFile[]
}

interface UploadedFile {
  name: string
  type: string
  size: number
  content?: string
  url?: string
}

interface FileNode {
  name: string
  type: "file" | "folder"
  children?: FileNode[]
  content?: string
}

export default function CustomIDE() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content:
        "Welcome to your Custom IDE! I can help you:\n\n• Clone any website or GitHub repository\n• Build fullstack applications\n• Debug and optimize code\n• Deploy to production\n\nWhat would you like to create today?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState("venice")
  const [activeTab, setActiveTab] = useState("chat")
  const [codeContent, setCodeContent] = useState("// Welcome to your custom IDE\n// Start coding here...")
  const [fileName, setFileName] = useState("app.tsx")
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [deploymentStatus, setDeploymentStatus] = useState<"idle" | "deploying" | "success" | "error">("idle")
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [fileTree, setFileTree] = useState<FileNode[]>([
    {
      name: "src",
      type: "folder",
      children: [
        { name: "app.tsx", type: "file", content: "// Welcome to your custom IDE\n// Start coding here..." },
        { name: "components", type: "folder", children: [] },
        { name: "utils", type: "folder", children: [] },
      ],
    },
  ])

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px"
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [input])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    const newFiles: UploadedFile[] = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]

      if (file.type.startsWith("image/")) {
        const url = URL.createObjectURL(file)
        newFiles.push({
          name: file.name,
          type: file.type,
          size: file.size,
          url: url,
        })
      } else if (file.type === "application/zip" || file.name.endsWith(".zip")) {
        const content = await file.text()
        newFiles.push({
          name: file.name,
          type: file.type,
          size: file.size,
          content: content,
        })
      } else {
        try {
          const content = await file.text()
          newFiles.push({
            name: file.name,
            type: file.type,
            size: file.size,
            content: content,
          })
        } catch (error) {
          newFiles.push({
            name: file.name,
            type: file.type,
            size: file.size,
          })
        }
      }
    }

    setUploadedFiles((prev) => [...prev, ...newFiles])

    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && uploadedFiles.length === 0) || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input.trim() || "Uploaded files for analysis",
      timestamp: new Date(),
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setUploadedFiles([])
    setIsLoading(true)

    try {
      const response = await fetch("/api/process-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          model: selectedModel,
          history: messages,
          files: userMessage.files,
        }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: data.response || "I apologize, but I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
        metadata: data.metadata,
      }

      setMessages((prev) => [...prev, assistantMessage])

      if (data.metadata?.code) {
        setCodeContent(data.metadata.code)
        setFileName(data.metadata.fileName || "app.tsx")
        setActiveTab("editor")
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    }

    setIsLoading(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleDeploy = async (platform: "vercel" | "github") => {
    setDeploymentStatus("deploying")

    try {
      const response = await fetch("/api/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform,
          code: codeContent,
          fileName,
          fileTree,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setDeploymentStatus("success")
        const deployMessage: Message = {
          id: Date.now().toString(),
          type: "assistant",
          content: `🚀 Successfully deployed to ${platform}!\n\nDeployment URL: ${data.url}\nGitHub Repository: ${data.repoUrl}`,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, deployMessage])
      } else {
        setDeploymentStatus("error")
      }
    } catch (error) {
      setDeploymentStatus("error")
    }

    setTimeout(() => setDeploymentStatus("idle"), 3000)
  }

  return (
    <div className="flex h-screen bg-background">
      <input ref={fileInputRef} type="file" multiple accept="*/*" onChange={handleFileUpload} className="hidden" />

      <div className="hidden md:flex w-64 lg:w-80 bg-sidebar border-r border-sidebar-border flex-col desktop-sidebar">
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-sidebar-primary rounded-lg">
              <Code className="w-4 h-4 text-sidebar-primary-foreground" />
            </div>
            <div>
              <h2 className="font-semibold text-sidebar-foreground">Custom IDE</h2>
              <p className="text-xs text-muted-foreground">AI-Powered</p>
            </div>
          </div>
        </div>

        <Tabs defaultValue="files" className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-4 bg-sidebar m-2">
            <TabsTrigger value="files" className="text-xs">
              <FolderTree className="w-3 h-3" />
            </TabsTrigger>
            <TabsTrigger value="integrations" className="text-xs">
              <Package className="w-3 h-3" />
            </TabsTrigger>
            <TabsTrigger value="overview" className="text-xs">
              <FileText className="w-3 h-3" />
            </TabsTrigger>
            <TabsTrigger value="deploy" className="text-xs">
              <Rocket className="w-3 h-3" />
            </TabsTrigger>
          </TabsList>

          <TabsContent value="files" className="flex-1 p-2">
            <div className="space-y-1">
              <div className="text-xs font-medium text-sidebar-foreground mb-2">File Explorer</div>
              {fileTree.map((node, index) => (
                <div key={index} className="flex items-center space-x-2 p-1 hover:bg-muted rounded text-sm">
                  <FolderTree className="w-3 h-3 text-sidebar-accent" />
                  <span className="text-sidebar-foreground">{node.name}</span>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="integrations" className="flex-1 p-2">
            <div className="space-y-2">
              <div className="text-xs font-medium text-sidebar-foreground mb-2">Integrations</div>
              <div className="space-y-1">
                <div className="flex items-center justify-between p-2 bg-card rounded border">
                  <div className="flex items-center space-x-2">
                    <Database className="w-3 h-3 text-sidebar-accent" />
                    <span className="text-xs">Supabase</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    Connected
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-card rounded border">
                  <div className="flex items-center space-x-2">
                    <Globe className="w-3 h-3 text-sidebar-accent" />
                    <span className="text-xs">Vercel</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    Connected
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-card rounded border">
                  <div className="flex items-center space-x-2">
                    <Code className="w-3 h-3 text-sidebar-accent" />
                    <span className="text-xs">GitHub</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    Connected
                  </Badge>
                </div>
              </div>
              <div className="mt-4 p-2 bg-card/50 rounded border border-dashed">
                <div className="text-xs font-medium text-sidebar-foreground mb-2">Automated Flow</div>
                <div className="text-xs text-muted-foreground">Supabase → GitHub → Vercel</div>
                <div className="text-xs text-muted-foreground mt-1">Auto-sync enabled</div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="overview" className="flex-1 p-2">
            <div className="space-y-2">
              <div className="text-xs font-medium text-sidebar-foreground mb-2">Project Overview</div>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div>Files: 3</div>
                <div>Components: 1</div>
                <div>Dependencies: 5</div>
                <div>Last modified: Just now</div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="deploy" className="flex-1 p-2">
            <div className="space-y-2">
              <div className="text-xs font-medium text-sidebar-foreground mb-2">Deployment</div>
              <Button
                size="sm"
                className="w-full bg-sidebar-primary hover:bg-sidebar-primary/90"
                onClick={() => handleDeploy("vercel")}
                disabled={deploymentStatus === "deploying"}
              >
                {deploymentStatus === "deploying" ? (
                  <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                ) : (
                  <Rocket className="w-3 h-3 mr-1" />
                )}
                Deploy to Vercel
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="w-full bg-transparent"
                onClick={() => handleDeploy("github")}
                disabled={deploymentStatus === "deploying"}
              >
                <Code className="w-3 h-3 mr-1" />
                Push to GitHub
              </Button>
              <Button size="sm" variant="outline" className="w-full bg-transparent">
                <Download className="w-3 h-3 mr-1" />
                Export Project
              </Button>
              {deploymentStatus !== "idle" && (
                <div className="text-xs text-center mt-2">
                  {deploymentStatus === "deploying" && "Deploying..."}
                  {deploymentStatus === "success" && "✅ Deployed successfully!"}
                  {deploymentStatus === "error" && "❌ Deployment failed"}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-sidebar border-t border-sidebar-border z-50 mobile-sidebar">
        <div className="flex justify-around p-2">
          <Button variant="ghost" size="sm" className="flex flex-col items-center space-y-1">
            <FolderTree className="w-4 h-4" />
            <span className="text-xs">Files</span>
          </Button>
          <Button variant="ghost" size="sm" className="flex flex-col items-center space-y-1">
            <Package className="w-4 h-4" />
            <span className="text-xs">Integrations</span>
          </Button>
          <Button variant="ghost" size="sm" className="flex flex-col items-center space-y-1">
            <FileText className="w-4 h-4" />
            <span className="text-xs">Overview</span>
          </Button>
          <Button variant="ghost" size="sm" className="flex flex-col items-center space-y-1">
            <Rocket className="w-4 h-4" />
            <span className="text-xs">Deploy</span>
          </Button>
        </div>
      </div>

      <div className="flex-1 flex flex-col main-content">
        <header className="border-b border-border bg-card/50 backdrop-blur-sm">
          <div className="px-2 md:px-4 py-3">
            <div className="flex items-center justify-between">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
                <TabsList className="bg-background">
                  <TabsTrigger value="chat" className="flex items-center space-x-1 md:space-x-2 text-xs md:text-sm">
                    <Bot className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden sm:inline">Chat</span>
                  </TabsTrigger>
                  <TabsTrigger value="editor" className="flex items-center space-x-1 md:space-x-2 text-xs md:text-sm">
                    <Code className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden sm:inline">Editor</span>
                  </TabsTrigger>
                  <TabsTrigger value="preview" className="flex items-center space-x-1 md:space-x-2 text-xs md:text-sm">
                    <Play className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden sm:inline">Preview</span>
                  </TabsTrigger>
                  <TabsTrigger value="terminal" className="flex items-center space-x-1 md:space-x-2 text-xs md:text-sm">
                    <Terminal className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden sm:inline">Terminal</span>
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              <div className="flex items-center space-x-2 md:space-x-3">
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger className="w-24 md:w-32 h-8 text-xs md:text-sm">
                    <div className="flex items-center space-x-1 md:space-x-2">
                      <Cpu className="w-3 h-3 text-primary" />
                      <SelectValue />
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="venice">Venice AI</SelectItem>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="gemini">Gemini</SelectItem>
                    <SelectItem value="llama">Llama</SelectItem>
                    <SelectItem value="deepseek">DeepSeek</SelectItem>
                  </SelectContent>
                </Select>

                <Badge variant="secondary" className="text-xs hidden sm:flex">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mr-1.5 animate-pulse"></div>
                  Active
                </Badge>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden">
          <Tabs value={activeTab} className="h-full flex flex-col">
            <TabsContent value="chat" className="flex-1 flex flex-col m-0">
              <div className="flex-1 overflow-y-auto">
                <div className="container mx-auto px-2 md:px-4 py-4 md:py-6 max-w-full md:max-w-4xl chat-container">
                  {messages.map((message) => (
                    <div key={message.id} className="flex gap-4">
                      <div className="flex-shrink-0">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            message.type === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-accent text-accent-foreground"
                          }`}
                        >
                          {message.type === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                        </div>
                      </div>

                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-foreground">
                            {message.type === "user" ? "You" : "AI Assistant"}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>

                        <Card className="bg-card border-border">
                          <CardContent className="p-4">
                            <div className="prose prose-sm max-w-none text-card-foreground">
                              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                                {message.content}
                              </pre>
                            </div>
                            {message.files && message.files.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-border">
                                <div className="text-xs font-medium text-muted-foreground mb-2">Attached Files:</div>
                                <div className="flex flex-wrap gap-2">
                                  {message.files.map((file, index) => (
                                    <div
                                      key={index}
                                      className="flex items-center space-x-2 bg-muted rounded-lg p-2 text-xs"
                                    >
                                      {file.type.startsWith("image/") ? (
                                        <ImageIcon className="w-3 h-3" />
                                      ) : file.name.endsWith(".zip") ? (
                                        <FileArchive className="w-3 h-3" />
                                      ) : (
                                        <FileText className="w-3 h-3" />
                                      )}
                                      <span className="truncate max-w-32">{file.name}</span>
                                      <span className="text-muted-foreground">({(file.size / 1024).toFixed(1)}KB)</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center">
                          <Bot className="w-4 h-4" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <Card className="bg-card border-border">
                          <CardContent className="p-4">
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span className="text-sm">AI is thinking...</span>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>

              <div className="border-t border-border bg-card/50 backdrop-blur-sm">
                <div className="container mx-auto px-2 md:px-4 py-3 md:py-4 max-w-full md:max-w-4xl">
                  {uploadedFiles.length > 0 && (
                    <div className="mb-3 p-3 bg-muted/50 rounded-lg border border-dashed">
                      <div className="text-xs font-medium text-foreground mb-2">Files to upload:</div>
                      <div className="flex flex-wrap gap-2">
                        {uploadedFiles.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center space-x-2 bg-background rounded-lg p-2 text-xs border"
                          >
                            {file.type.startsWith("image/") ? (
                              <ImageIcon className="w-3 h-3" />
                            ) : file.name.endsWith(".zip") ? (
                              <FileArchive className="w-3 h-3" />
                            ) : (
                              <FileText className="w-3 h-3" />
                            )}
                            <span className="truncate max-w-32">{file.name}</span>
                            <span className="text-muted-foreground">({(file.size / 1024).toFixed(1)}KB)</span>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-4 w-4 p-0 hover:bg-destructive hover:text-destructive-foreground"
                              onClick={() => removeFile(index)}
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="flex gap-3">
                    <div className="flex-1 relative">
                      <Textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Tell me what you'd like to build, clone, or enhance..."
                        className="min-h-[44px] max-h-[200px] resize-none bg-background border-border pr-20"
                        rows={1}
                      />
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => fileInputRef.current?.click()}
                        className="absolute right-12 bottom-2 h-8 w-8 p-0 hover:bg-muted"
                      >
                        <Paperclip className="w-4 h-4" />
                      </Button>
                      <Button
                        type="submit"
                        size="sm"
                        disabled={(!input.trim() && uploadedFiles.length === 0) || isLoading}
                        className="absolute right-2 bottom-2 h-8 w-8 p-0 bg-primary hover:bg-primary/90"
                      >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      </Button>
                    </div>
                  </form>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="editor" className="flex-1 flex flex-col m-0">
              <div className="border-b border-border bg-card/50 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-foreground">{fileName}</span>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" variant="outline" className="h-7 text-xs bg-transparent">
                      <Save className="w-3 h-3 mr-1" />
                      Save
                    </Button>
                    <Button size="sm" variant="outline" className="h-7 text-xs bg-transparent">
                      <RefreshCw className="w-3 h-3 mr-1" />
                      Format
                    </Button>
                  </div>
                </div>
              </div>
              <div className="flex-1 bg-slate-900 text-slate-100 p-4 font-mono text-sm overflow-auto">
                <textarea
                  value={codeContent}
                  onChange={(e) => setCodeContent(e.target.value)}
                  className="w-full h-full bg-transparent border-none outline-none resize-none"
                  spellCheck={false}
                />
              </div>
            </TabsContent>

            <TabsContent value="preview" className="flex-1 m-0">
              <div className="h-full bg-white border border-border rounded-lg m-4 flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <Play className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Preview will appear here when you run your code</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="terminal" className="flex-1 m-0">
              <div className="h-full bg-slate-900 text-slate-100 p-4 font-mono text-sm">
                <div className="text-green-400">$ Welcome to Custom IDE Terminal</div>
                <div className="text-gray-400">Ready for commands...</div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
