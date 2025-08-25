import { type NextRequest, NextResponse } from "next/server"
import { MODEL_CONFIGS } from "@/config/api-keys"

export async function POST(request: NextRequest) {
  try {
    const { message, model, history, files } = await request.json()

    let response = ""
    let metadata: any = {}

    if (files && files.length > 0) {
      const fileTypes = files.map((f: any) => f.type).join(", ")
      const fileNames = files.map((f: any) => f.name).join(", ")

      if (files.some((f: any) => f.type.startsWith("image/"))) {
        response = `🖼️ Analyzing uploaded images...\n\nI can see you've uploaded: ${fileNames}\n\nI'm processing these images to:\n• Extract design patterns and layouts\n• Generate corresponding code\n• Create responsive components\n• Optimize for web performance\n\nThe generated code will be available in your IDE workspace.`
        metadata = { openIDE: true, type: "image-analysis", files }
      } else if (files.some((f: any) => f.name.endsWith(".zip"))) {
        response = `📦 Processing uploaded ZIP file...\n\nI'm extracting and analyzing: ${fileNames}\n\nProcessing steps:\n• Extract ZIP contents\n• Analyze project structure\n• Set up development environment\n• Import into IDE workspace\n\nYour project will be ready for editing shortly.`
        metadata = { openIDE: true, type: "zip-extraction", files }
      } else if (files.some((f: any) => f.name.includes("figma") || f.type.includes("figma"))) {
        response = `🎨 Processing Figma design...\n\nI'm converting your Figma design to code:\n• Extract design tokens and components\n• Generate React/HTML components\n• Apply responsive design patterns\n• Create production-ready code\n\nThe converted design will open in your IDE workspace.`
        metadata = { openIDE: true, type: "figma-conversion", files }
      } else {
        response = `📁 Processing uploaded files...\n\nI've received: ${fileNames}\n\nI'm analyzing the files to:\n• Understand the project structure\n• Generate missing components\n• Optimize and enhance the code\n• Set up the development environment\n\nThe processed project will be available in your IDE workspace.`
        metadata = { openIDE: true, type: "file-analysis", files }
      }
    } else if (message.toLowerCase().includes("clone") && (message.includes("http") || message.includes("github"))) {
      if (message.includes("github.com")) {
        response = `🔄 Cloning GitHub repository...\n\nI'm analyzing the repository structure and preparing to:\n• Clone the repository locally\n• Analyze the codebase architecture\n• Set up the development environment\n• Open the project in VSCode.dev\n\nThe repository will be available in your IDE workspace shortly.`
        metadata = { openIDE: true, type: "github", url: extractUrl(message) }
      } else {
        response = `🌐 Cloning website...\n\nI'm analyzing the website and preparing to:\n• Scrape the website structure and content\n• Generate clean, modern code\n• Set up responsive design\n• Create optimized assets\n• Open the project in VSCode.dev\n\nThe cloned website will be available in your IDE workspace shortly.`
        metadata = { openIDE: true, type: "website", url: extractUrl(message) }
      }
    } else if (message.toLowerCase().includes("build") && message.toLowerCase().includes("app like")) {
      const appName = extractAppName(message)
      response = `🚀 Building an app like ${appName}...\n\nI'm creating a comprehensive application with:\n• Modern UI/UX design\n• Full authentication system\n• Database integration\n• API endpoints\n• Responsive design\n• Production-ready deployment\n\nThe project structure will be set up in your IDE workspace.`
      metadata = { openIDE: true, type: "build", appName }
    } else if (message.toLowerCase().includes("debug") || message.toLowerCase().includes("fix")) {
      response = `🔧 Analyzing code for debugging...\n\nI'm examining the codebase to:\n• Identify potential issues\n• Suggest optimizations\n• Fix bugs and errors\n• Improve performance\n• Update dependencies\n\nI'll provide detailed solutions and open the fixed code in your IDE.`
      metadata = { openIDE: true, type: "debug" }
    } else {
      response = `💡 I can help you with that!\n\nAs your AI Fullstack Developer, I can:\n• Clone any website or GitHub repository\n• Build applications from scratch\n• Debug and optimize existing code\n• Create modern, responsive interfaces\n• Set up databases and APIs\n• Deploy to production\n\nPlease provide more specific details about what you'd like me to help you with.`
    }

    const selectedModel = MODEL_CONFIGS[model as keyof typeof MODEL_CONFIGS] || MODEL_CONFIGS.venice

    return NextResponse.json({
      response,
      metadata: {
        ...metadata,
        modelUsed: selectedModel.name,
        provider: selectedModel.provider,
      },
      model: model || "venice",
    })
  } catch (error) {
    console.error("Error processing request:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}

function extractUrl(message: string): string {
  const urlRegex = /(https?:\/\/[^\s]+)/g
  const match = message.match(urlRegex)
  return match ? match[0] : ""
}

function extractAppName(message: string): string {
  const match = message.match(/app like (\w+)/i)
  return match ? match[1] : "the requested application"
}
