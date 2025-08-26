import { Chart } from "@/components/ui/chart"
class SmartArmDashboard {
  constructor() {
    this.mqttClient = null
    this.websocket = null
    this.isConnected = false
    this.currentMode = "auto"
    this.chart = null
    this.startTime = Date.now()
    this.eventLog = []
    this.systemData = {
      grabCount: 0,
      successRate: 0,
      distance: 0,
      motorSpeed: 0,
      servoAngles: [90, 90, 90, 90, 90],
      lastDetection: null,
    }

    this.init()
  }

  init() {
    this.setupEventListeners()
    this.initializeChart()
    this.connectWebSocket()
    this.startUpdateLoop()
    this.loadTheme()

    // Add initial event
    this.addEvent("System initialized", "info")
  }

  setupEventListeners() {
    // Theme toggle
    document.getElementById("themeToggle").addEventListener("click", () => {
      this.toggleTheme()
    })

    // Mode toggle
    document.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        this.setMode(e.target.dataset.mode)
      })
    })

    // Servo controls
    document.querySelectorAll(".servo-slider").forEach((slider) => {
      slider.addEventListener("input", (e) => {
        this.updateServoValue(e.target)
      })

      slider.addEventListener("change", (e) => {
        this.sendServoCommand(e.target.dataset.servo, e.target.value)
      })
    })

    // Direction controls
    document.querySelectorAll(".direction-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        if (e.target.dataset.direction) {
          this.sendDirectionCommand(e.target.dataset.direction)
        } else if (e.target.dataset.action === "grab") {
          this.sendGrabCommand()
        }
      })
    })

    // Emergency stop
    document.getElementById("emergencyStop").addEventListener("click", () => {
      this.emergencyStop()
    })

    // Chart period controls
    document.querySelectorAll(".chart-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        this.updateChartPeriod(e.target.dataset.period)
      })
    })

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (this.currentMode === "manual") {
        this.handleKeyboardControl(e)
      }
    })
  }

  connectWebSocket() {
    try {
      this.websocket = new WebSocket("ws://localhost:8765")

      this.websocket.onopen = () => {
        this.updateConnectionStatus(true)
        this.addEvent("WebSocket connected", "success")
      }

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleWebSocketMessage(data)
      }

      this.websocket.onclose = () => {
        this.updateConnectionStatus(false)
        this.addEvent("WebSocket disconnected", "warning")
        // Attempt to reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000)
      }

      this.websocket.onerror = (error) => {
        console.error("WebSocket error:", error)
        this.addEvent("WebSocket error", "error")
      }
    } catch (error) {
      console.error("Failed to connect WebSocket:", error)
      this.addEvent("Failed to connect WebSocket", "error")
      // Retry connection
      setTimeout(() => this.connectWebSocket(), 5000)
    }
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case "status":
        this.updateSystemStatus(data.data)
        break
      case "detections":
        this.handleDetections(data.data)
        break
      case "event":
        this.addEvent(data.message, data.level || "info")
        break
    }
  }

  updateSystemStatus(status) {
    this.systemData = { ...this.systemData, ...status }

    // Update UI elements
    document.getElementById("distance").textContent = status.distance_cm?.toFixed(1) || "0.0"
    document.getElementById("motorSpeed").textContent = status.motor_speed || "0"
    document.getElementById("currentMode").textContent = status.mode === "auto" ? "Automatic" : "Manual"

    // Update servo displays
    if (status.servo_angles) {
      status.servo_angles.forEach((angle, index) => {
        const slider = document.querySelector(`[data-servo="${index}"]`)
        if (slider && this.currentMode === "auto") {
          slider.value = angle
          this.updateServoValue(slider)
        }
      })
    }
  }

  handleDetections(detections) {
    if (detections && detections.length > 0) {
      const detection = detections[0] // Use first detection
      this.systemData.lastDetection = detection.class_name
      document.getElementById("lastDetection").textContent = detection.class_name

      this.addEvent(`Detected: ${detection.class_name} (${(detection.confidence * 100).toFixed(1)}%)`, "info")
    }
  }

  setMode(mode) {
    this.currentMode = mode

    // Update UI
    document.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.mode === mode)
    })

    const manualControls = document.getElementById("manualControls")
    manualControls.classList.toggle("active", mode === "manual")

    // Send command to backend
    this.sendCommand("set_mode", { mode })

    this.addEvent(`Switched to ${mode} mode`, "info")
  }

  updateServoValue(slider) {
    const valueSpan = slider.parentElement.querySelector(".servo-value")
    valueSpan.textContent = `${slider.value}°`
  }

  sendServoCommand(servoId, angle) {
    if (this.currentMode !== "manual") return

    this.sendCommand("manual_servo", {
      servo_id: Number.parseInt(servoId),
      angle: Number.parseInt(angle),
    })

    this.addEvent(`Servo ${servoId} moved to ${angle}°`, "info")
  }

  sendDirectionCommand(direction) {
    if (this.currentMode !== "manual") return

    const movements = {
      up: { servo_id: 1, angle: -10 },
      down: { servo_id: 1, angle: 10 },
      left: { servo_id: 0, angle: -10 },
      right: { servo_id: 0, angle: 10 },
    }

    const movement = movements[direction]
    if (movement) {
      const currentSlider = document.querySelector(`[data-servo="${movement.servo_id}"]`)
      const newAngle = Math.max(0, Math.min(180, Number.parseInt(currentSlider.value) + movement.angle))

      currentSlider.value = newAngle
      this.updateServoValue(currentSlider)
      this.sendServoCommand(movement.servo_id, newAngle)
    }
  }

  sendGrabCommand() {
    if (this.currentMode !== "manual") return

    // Close gripper (servo 4 to 180)
    const gripperSlider = document.querySelector('[data-servo="4"]')
    if (gripperSlider) {
      gripperSlider.value = 180
      this.updateServoValue(gripperSlider)
      this.sendServoCommand(4, 180)
    }

    this.addEvent("Grab command executed", "success")
  }

  emergencyStop() {
    this.sendCommand("emergency_stop", {})
    this.addEvent("EMERGENCY STOP activated", "error")
    this.showNotification("Emergency stop activated!", "error")
  }

  sendCommand(command, data) {
    fetch("/api/control", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command, ...data }),
    })
      .then((response) => response.json())
      .then((result) => {
        if (!result.success && result.error) {
          this.addEvent(`Command failed: ${result.error}`, "error")
        }
      })
      .catch((error) => {
        console.error("Command error:", error)
        this.addEvent(`Command error: ${error.message}`, "error")
      })
  }

  handleKeyboardControl(e) {
    if (this.currentMode !== "manual") return

    const keyMap = {
      ArrowUp: "up",
      ArrowDown: "down",
      ArrowLeft: "left",
      ArrowRight: "right",
      " ": "grab", // Spacebar
      Escape: "stop",
    }

    const action = keyMap[e.key]
    if (action) {
      e.preventDefault()

      if (action === "grab") {
        this.sendGrabCommand()
      } else if (action === "stop") {
        this.emergencyStop()
      } else {
        this.sendDirectionCommand(action)
      }
    }
  }

  initializeChart() {
    const ctx = document.getElementById("operationsChart").getContext("2d")

    this.chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Successful Operations",
            data: [],
            borderColor: "rgb(34, 197, 94)",
            backgroundColor: "rgba(34, 197, 94, 0.1)",
            tension: 0.4,
          },
          {
            label: "Total Operations",
            data: [],
            borderColor: "rgb(99, 102, 241)",
            backgroundColor: "rgba(99, 102, 241, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          x: {
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
        },
      },
    })

    this.loadChartData("daily")
  }

  updateChartPeriod(period) {
    document.querySelectorAll(".chart-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.period === period)
    })

    this.loadChartData(period)
  }

  async loadChartData(period) {
    try {
      const days = period === "daily" ? 7 : period === "weekly" ? 30 : 365
      const response = await fetch(`/api/statistics?days=${days}`)
      const data = await response.json()

      if (data.daily_operations) {
        const labels = Object.keys(data.daily_operations)
        const values = Object.values(data.daily_operations)

        // Simulate success data (in real implementation, this would come from backend)
        const successValues = values.map((v) => Math.floor(v * 0.8)) // 80% success rate simulation

        this.chart.data.labels = labels
        this.chart.data.datasets[0].data = successValues
        this.chart.data.datasets[1].data = values
        this.chart.update()
      }

      // Update statistics
      if (data.success_rate !== undefined) {
        document.getElementById("successRate").textContent = `${data.success_rate.toFixed(1)}%`
      }
      if (data.total_operations !== undefined) {
        document.getElementById("grabCount").textContent = data.total_operations
      }
    } catch (error) {
      console.error("Failed to load chart data:", error)
      this.addEvent("Failed to load chart data", "error")
    }
  }

  addEvent(message, type = "info") {
    const event = {
      message,
      type,
      timestamp: new Date(),
    }

    this.eventLog.unshift(event)

    // Keep only last 50 events
    if (this.eventLog.length > 50) {
      this.eventLog = this.eventLog.slice(0, 50)
    }

    this.updateEventLog()
  }

  updateEventLog() {
    const eventLogContainer = document.getElementById("eventLog")

    // Show only last 5 events
    const recentEvents = this.eventLog.slice(0, 5)

    eventLogContainer.innerHTML = recentEvents
      .map(
        (event) => `
            <div class="event-item">
                <div class="event-content">
                    <div class="event-message">${event.message}</div>
                    <div class="event-time">${event.timestamp.toLocaleTimeString()}</div>
                </div>
                <div class="event-type ${event.type}">${event.type.toUpperCase()}</div>
            </div>
        `,
      )
      .join("")
  }

  updateConnectionStatus(connected) {
    this.isConnected = connected
    const statusElement = document.getElementById("connectionStatus")
    const textElement = document.getElementById("connectionText")

    if (connected) {
      statusElement.className = "connection-status connected"
      textElement.textContent = "Connected"
    } else {
      statusElement.className = "connection-status disconnected"
      textElement.textContent = "Disconnected"
    }
  }

  showNotification(message, type = "info") {
    const container = document.getElementById("notificationContainer")
    const notification = document.createElement("div")
    notification.className = `notification ${type}`
    notification.innerHTML = `
            <div>${message}</div>
        `

    container.appendChild(notification)

    // Show notification
    setTimeout(() => notification.classList.add("show"), 100)

    // Remove notification after 5 seconds
    setTimeout(() => {
      notification.classList.remove("show")
      setTimeout(() => container.removeChild(notification), 300)
    }, 5000)
  }

  toggleTheme() {
    const body = document.body
    const isDark = body.classList.toggle("dark")
    const themeIcon = document.getElementById("themeIcon")

    themeIcon.textContent = isDark ? "☀️" : "🌙"
    localStorage.setItem("theme", isDark ? "dark" : "light")

    this.addEvent(`Switched to ${isDark ? "dark" : "light"} theme`, "info")
  }

  loadTheme() {
    const savedTheme = localStorage.getItem("theme")
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    const isDark = savedTheme === "dark" || (!savedTheme && prefersDark)

    if (isDark) {
      document.body.classList.add("dark")
      document.getElementById("themeIcon").textContent = "☀️"
    }
  }

  updateUptime() {
    const uptime = Date.now() - this.startTime
    const hours = Math.floor(uptime / (1000 * 60 * 60))
    const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((uptime % (1000 * 60)) / 1000)

    document.getElementById("uptime").textContent =
      `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
  }

  startUpdateLoop() {
    setInterval(() => {
      this.updateUptime()

      // Fetch latest statistics periodically
      if (this.isConnected) {
        this.loadChartData("daily")
      }
    }, 1000)
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new SmartArmDashboard()
})

// Handle page visibility changes
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    // Page is hidden, reduce update frequency
    console.log("Dashboard hidden, reducing updates")
  } else {
    // Page is visible, resume normal updates
    console.log("Dashboard visible, resuming updates")
    if (window.dashboard) {
      window.dashboard.loadChartData("daily")
    }
  }
})
