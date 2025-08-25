import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { apiKey } = await request.json()

    if (!apiKey) {
      return NextResponse.json({ error: "API key is required" }, { status: 400 })
    }

    // Store API key securely (in production, use proper encryption)
    // For now, we'll just validate it's provided
    console.log("[v0] Venice AI API key configured")

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[v0] Error configuring API key:", error)
    return NextResponse.json({ error: "Failed to configure API key" }, { status: 500 })
  }
}
