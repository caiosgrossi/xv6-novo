#!/usr/bin/env python3
import os
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Paths
repo = os.getcwd()
outpdf = os.path.join(repo, 'tools', 'report_lottery_scheduler.pdf')
plot_candidates = [
    'tools/lottery_smp1_120.png',
    'tools/lottery_smp1_600_extended.png',
    'tools/lottery_smp1_long.png',
    'tools/lottery_smp1_600.png',
    'tools/lottery_smp1_long.png',
    'tools/lottery_smp1_120.png'
]
# Files to include diffs for
files = ['kernel/proc.h','kernel/proc.c','kernel/pstat.h','kernel/sysproc.c','user/pstat.h','user/lotterytest.c','tools/plot_lottery.py','user/ps.c','user/usys.pl','user/init.c','Makefile']

# Collect git diff
try:
    diff = subprocess.check_output(['git','--no-pager','diff','-U0','--']+files, stderr=subprocess.STDOUT).decode('utf-8')
except subprocess.CalledProcessError as e:
    diff = e.output.decode('utf-8') if e.output else 'Could not collect git diff.'

# Choose plot if available
plot_path = None
for p in plot_candidates:
    if os.path.exists(os.path.join(repo,p)):
        plot_path = os.path.join(repo,p)
        break

# Compose report text in Portuguese (passive voice)
summary = '''Relatório: Implementação do Escalonador por Loteria no xv6

Resumo das alterações (voz passiva):
- Foi adicionada a estrutura para armazenar bilhetes e contadores por processo (`tickets`, `ticks`).
- Foi implementado um gerador pseudo-aleatório (LCG) e a seleção por bilhete na rotina de escalonamento, substituindo o escalonador original.
- Foram adicionadas as syscalls `settickets(int)` e `getpinfo(struct pstat *)`; a segunda preenche a estrutura `pstat` com informação de processos.
- Foram adicionados programas de utilizador (`ps`, `lotterytest`) e uma ferramenta de geração de gráficos (`tools/plot_lottery.py`).

Como a estrutura `pstat` foi preenchida:
- Para cada slot da tabela de processos (`proc[]`) foi lido sob proteção do respectivo lock:
  - `inuse[i]` foi definido segundo se o slot estava em uso;
  - `tickets[i]`, `pid[i]` e `ticks[i]` foram copiados para a estrutura kernel;
- A estrutura kernel foi copiada para o espaço de utilizador com `copyout`.

Observações sobre testes:
- O teste foi executado em ambiente QEMU com um único CPU (`-smp 1`) para evidenciar a justiça global do algoritmo.
- Foram usados testes de curta e longa duração; os resultados foram amostrados e apresentados nos gráficos incluídos.
'''

# Create PDF
with PdfPages(outpdf) as pdf:
    # Page 1: summary text
    fig = plt.figure(figsize=(8.27,11.69))  # A4
    fig.clf()
    plt.axis('off')
    plt.text(0.01,0.99,'Relatório: Escalonador por Loteria no xv6', fontsize=16, weight='bold', va='top')
    plt.text(0.01,0.92,summary, fontsize=10, va='top')
    pdf.savefig(fig)
    plt.close(fig)

    # Page 2: plot image if present
    if plot_path:
        try:
            img = mpimg.imread(plot_path)
            fig = plt.figure(figsize=(11,8.5))
            plt.imshow(img)
            plt.axis('off')
            plt.title('Gráfico de ticks amostrados')
            pdf.savefig(fig)
            plt.close(fig)
        except Exception as e:
            fig = plt.figure(figsize=(8.27,11.69))
            plt.axis('off')
            plt.text(0.01,0.99,'Erro ao incluir imagem: '+str(e), fontsize=10, va='top')
            pdf.savefig(fig)
            plt.close(fig)

    # Page(s) for diffs: split into chunks
    if diff:
        lines = diff.splitlines()
        chunk_size = 60
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i+chunk_size])
            fig = plt.figure(figsize=(8.27,11.69))
            plt.axis('off')
            plt.text(0.01,0.99,chunk, fontsize=7, family='monospace', va='top')
            pdf.savefig(fig)
            plt.close(fig)

print('PDF gerado em:', outpdf)
