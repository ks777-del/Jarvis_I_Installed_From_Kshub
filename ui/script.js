(() => {
    const statusEl = document.getElementById("status");
    const taskEl = document.getElementById("task");
    const waveformEl = document.getElementById("waveform");
    const logEl = document.getElementById("message-log");
    const inputEl = document.getElementById("command-input");
    const sendBtn = document.getElementById("send-btn");
    const newChatBtn = document.getElementById("new-chat-btn");
    const fileUploadBtn = document.getElementById("file-upload-btn");
    const pptBtn = document.getElementById("ppt-btn");
    const settingsBtn = document.getElementById("settings-btn");
    const particlesEl = document.getElementById("particles");
    const loaderEl = document.getElementById("loader");
    const progressWrapEl = document.getElementById("progress-wrap");
    const progressBarEl = document.getElementById("progress-bar");
    const downloadWrapEl = document.getElementById("download-wrap");
    const downloadBtnEl = document.getElementById("download-btn");
    const gamesListEl = document.getElementById("games-list");
    let downloadPath = "";
    let settingsVisible = false;

    let currentState = "idle";
    const bars = [];
    const BAR_COUNT = 56;

    function setupWaveform() {
        for (let i = 0; i < BAR_COUNT; i += 1) {
            const bar = document.createElement("div");
            bar.className = "wave-bar";
            bar.style.height = "10px";
            waveformEl.appendChild(bar);
            bars.push(bar);
        }
    }

    function setupParticles() {
        for (let i = 0; i < 42; i += 1) {
            const dot = document.createElement("div");
            dot.className = "particle";
            dot.style.left = `${Math.random() * 100}%`;
            dot.style.animationDuration = `${8 + Math.random() * 10}s`;
            dot.style.animationDelay = `${-Math.random() * 12}s`;
            particlesEl.appendChild(dot);
        }
    }

    function animateWaveform() {
        let t = 0;

        function frame() {
            const amp = currentState === "speaking"
                ? 28
                : currentState === "listening"
                    ? 18
                    : currentState === "thinking"
                        ? 12
                        : 8;

            for (let i = 0; i < bars.length; i += 1) {
                const noise = Math.sin((t + i) * 0.23) + Math.cos((t + i) * 0.11);
                const height = 10 + Math.max(1, (noise + 2) * amp * 0.22);
                bars[i].style.height = `${Math.min(56, height)}px`;
            }

            t += 1;
            window.requestAnimationFrame(frame);
        }

        window.requestAnimationFrame(frame);
    }

    function classifyStatus(text) {
        const lower = String(text || "").toLowerCase();
        if (lower.includes("listen")) return "listening";
        if (lower.includes("speak")) return "speaking";
        if (lower.includes("think")) return "thinking";
        return "idle";
    }

    function fadeTask(nextText) {
        taskEl.classList.add("fade");
        window.setTimeout(() => {
            taskEl.textContent = nextText || "";
            taskEl.classList.remove("fade");
        }, 160);
    }

    window.setTask = (text) => {
        fadeTask(String(text || ""));
    };

    window.setStatus = (text) => {
        const clean = String(text || "Idle");
        currentState = classifyStatus(clean);
        statusEl.className = currentState;
        statusEl.textContent = clean;
    };

    window.addMessage = (sender, text) => {
        const line = document.createElement("div");
        line.className = "msg";
        line.textContent = `${sender}: ${text}`;
        logEl.prepend(line);

        while (logEl.children.length > 6) {
            logEl.removeChild(logEl.lastChild);
        }

        window.setTimeout(() => {
            line.style.opacity = "0";
            line.style.transform = "translateY(-6px)";
        }, 5200);
    };

    window.setLoader = (active, text) => {
        const enabled = Boolean(active);
        loaderEl.textContent = text || "Working...";
        loaderEl.className = enabled ? "" : "hidden";
        progressWrapEl.className = enabled ? "" : "hidden";
        if (!enabled) {
            progressBarEl.style.width = "0%";
        }
    };

    window.setProgress = (value) => {
        const clean = Math.max(0, Math.min(Number(value || 0), 100));
        progressBarEl.style.width = `${clean}%`;
    };

    window.setDownload = (label, path) => {
        downloadPath = String(path || "");
        if (!downloadPath) {
            downloadWrapEl.className = "hidden";
            return;
        }
        downloadBtnEl.textContent = String(label || "Download");
        downloadWrapEl.className = "";
    };

    function emitCommandToPython(text) {
        const value = String(text || "").trim();
        if (!value) return;

        if (window.pyBridge && typeof window.pyBridge.submitText === "function") {
            window.pyBridge.submitText(value);
        }

        inputEl.value = "";
        window.setTask(`Command: ${value}`);
    }

    sendBtn.addEventListener("click", () => emitCommandToPython(inputEl.value));
    newChatBtn.addEventListener("click", () => {
        logEl.innerHTML = "";
        window.setTask("New chat started.");
        window.addMessage("System", "Chat reset.");
    });
    fileUploadBtn.addEventListener("click", () => {
        if (window.pyBridge && typeof window.pyBridge.requestFileUpload === "function") {
            window.pyBridge.requestFileUpload();
        } else {
            window.addMessage("System", "File upload bridge is unavailable.");
        }
    });
    pptBtn.addEventListener("click", () => {
        const topic = window.prompt("Enter PPT topic");
        if (!topic) return;
        emitCommandToPython(`create ppt on ${topic}`);
    });
    settingsBtn.addEventListener("click", () => {
        settingsVisible = !settingsVisible;
        const display = settingsVisible ? "none" : "";
        document.querySelectorAll(".panel").forEach((panel) => {
            panel.style.display = display;
        });
        window.setTask(settingsVisible ? "Settings mode: side panels hidden." : "Settings mode: side panels visible.");
    });
    downloadBtnEl.addEventListener("click", () => {
        if (!downloadPath) return;
        if (window.pyBridge && typeof window.pyBridge.openLocalFile === "function") {
            window.pyBridge.openLocalFile(downloadPath);
        }
        window.addMessage("Jarvis", `PPT file ready at: ${downloadPath}`);
    });
    inputEl.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            emitCommandToPython(inputEl.value);
        }
    });
    gamesListEl.addEventListener("click", (event) => {
        const item = event.target.closest("li");
        if (!item) return;
        const text = String(item.textContent || "").trim().toLowerCase();
        if (!text) return;
        emitCommandToPython(text);
    });

    function initWebChannel() {
        if (typeof QWebChannel === "undefined" || !window.qt || !window.qt.webChannelTransport) {
            return;
        }

        // eslint-disable-next-line no-undef
        new QWebChannel(window.qt.webChannelTransport, (channel) => {
            window.pyBridge = channel.objects.bridge;
            if (!window.pyBridge) return;

            if (window.pyBridge.statusChanged) {
                window.pyBridge.statusChanged.connect((text) => window.setStatus(text));
            }
            if (window.pyBridge.taskChanged) {
                window.pyBridge.taskChanged.connect((text) => window.setTask(text));
            }
            if (window.pyBridge.messageAdded) {
                window.pyBridge.messageAdded.connect((sender, text) => window.addMessage(sender, text));
            }
            if (window.pyBridge.loaderChanged) {
                window.pyBridge.loaderChanged.connect((active, text) => window.setLoader(active, text));
            }
            if (window.pyBridge.downloadReady) {
                window.pyBridge.downloadReady.connect((label, path) => window.setDownload(label, path));
            }
            if (window.pyBridge.progressChanged) {
                window.pyBridge.progressChanged.connect((value) => window.setProgress(value));
            }
        });
    }

    setupWaveform();
    setupParticles();
    animateWaveform();
    initWebChannel();
    window.setStatus("Idle");
    window.setTask("System ready.");
})();
