interface StreamEvent {
    title: string
    title_url: string
    type: string
    user: string
    comment: string
    timestamp: number
    wikiprojects: string[]
}

class Project {
    name: string
    count: number
    lastEvent: StreamEvent

    constructor(name: string, count: number, lastEvent: StreamEvent){
        this.name = name
        this.count = count
        this.lastEvent = lastEvent
    }
}

const PROJECTS = new Map<string, Project>()


const eventSource = new EventSource("/events")

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data) as StreamEvent
    data.wikiprojects.forEach(name => {
        const current = PROJECTS.get(name) || new Project(name, 0, data)
        current!.count++
        current!.lastEvent = data
        PROJECTS.set(name, current)
    })

    render()
}

eventSource.onerror = (error) => {
    console.log("Error: " + error)
}

function render() {
    const sortedProjects = [...PROJECTS.values()].sort(
        (a, b) => b.count - a.count
    )
    
    const tbody = document.getElementById("ranking-table")?.getElementsByTagName("tbody")[0]
    tbody!.innerHTML = ""

    sortedProjects.forEach((project, index) => {
        const tr = tbody?.insertRow()
        
        const tdRanking = tr?.insertCell(0)
        tdRanking!.textContent = (index+1).toString()
        tdRanking!.className = "align-right"
        
        const tdProject = tr?.insertCell(1)
        const projectAnchor = document.createElement("a")
        projectAnchor.href = getProjectUrl(project.name).href
        projectAnchor.textContent = project.name
        projectAnchor.target = "_blank"
        tdProject?.appendChild(projectAnchor)
        
        const tdLatestTitle = tr?.insertCell(2)
        const a = document.createElement("a")
        a.href = project.lastEvent.title_url
        a.textContent = project.lastEvent.title
        a.target = "_blank" // open link in new tab
        tdLatestTitle!.appendChild(a)

        const tdCount = tr?.insertCell(3)
        tdCount!.textContent = project.count.toString()
        tdCount!.className = "align-right"

        const tdBar = tr?.insertCell(4)
        const width = 100*(project.count / sortedProjects[0]!.count)
        tdBar!.appendChild(createBar(width))
    })
}

function createBar(widthPercentage: number): HTMLDivElement {
    const div = document.createElement("div") as HTMLDivElement
    div.className = "bar"
    div.style.width = `${widthPercentage}%`
    return div
}

function getProjectUrl(name: string): URL {
    return new URL(`https://en.wikipedia.org/wiki/Wikipedia:WikiProject_${name.replace(" ", "_")}`)
}