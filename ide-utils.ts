export const openIDEWorkspace = (metadata: any) => {
  // Create a unique workspace identifier
  const workspaceId = `workspace-${Date.now()}`

  // If we have code content, we could potentially save it to localStorage
  // or send it to a backend service for persistence
  if (metadata?.code) {
    localStorage.setItem(`${workspaceId}-code`, metadata.code)
    localStorage.setItem(`${workspaceId}-fileName`, metadata.fileName || "app.tsx")
  }

  // For now, open VSCode.dev with a folder structure
  const vscodeUrl = `https://vscode.dev/?folder=/tmp/${workspaceId}`
  window.open(vscodeUrl, "_blank")

  // Return workspace info for potential future use
  return {
    workspaceId,
    url: vscodeUrl,
    metadata,
  }
}

// Additional utility functions for IDE integration
export const saveCodeToWorkspace = (code: string, fileName: string, workspaceId?: string) => {
  const id = workspaceId || `workspace-${Date.now()}`
  localStorage.setItem(`${id}-code`, code)
  localStorage.setItem(`${id}-fileName`, fileName)
  return id
}

export const loadCodeFromWorkspace = (workspaceId: string) => {
  const code = localStorage.getItem(`${workspaceId}-code`)
  const fileName = localStorage.getItem(`${workspaceId}-fileName`)
  return { code, fileName }
}

export const createWorkspaceFromFiles = (files: { name: string; content: string }[]) => {
  const workspaceId = `workspace-${Date.now()}`

  files.forEach((file, index) => {
    localStorage.setItem(`${workspaceId}-file-${index}`, JSON.stringify(file))
  })

  localStorage.setItem(`${workspaceId}-fileCount`, files.length.toString())

  return workspaceId
}
