from src.gantt import GanttChart

if __name__ == "__main__":
    chart = GanttChart()
    
    chart.adicionar_intervalo('Task 1', 2, 5, '#F00')
    chart.adicionar_intervalo('Task 1', 9, 15, '#F00')
    
    chart.adicionar_intervalo('Task 2', 0, 3, '#0F0')
    chart.adicionar_intervalo('Task 2', 5, 7, '#0F0')
    
    chart.adicionar_intervalo('Task 3', 0, 20, '#00F')

    chart.exibir_terminal()