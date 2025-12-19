<h1>Phase – Calculadora de Correntes de Fase</h1>

<p>
  O <strong>Phase</strong> é uma aplicação desenvolvida em <strong>Python</strong> com interface gráfica 
  em <strong>Tkinter</strong> que permite calcular e visualizar o diagrama fasorial das correntes 
  de um sistema elétrico trifásico. O software auxilia na análise de equilíbrio de cargas e 
  no dimensionamento de sistemas elétricos de baixa tensão.
</p>

<h2>Descrição Geral</h2>
<p>
  O programa possibilita adicionar múltiplas cargas, especificando o nome, potência, tensão 
  e fases envolvidas (<strong>R</strong>, <strong>S</strong>, <strong>T</strong> e <strong>Neutro</strong>). 
  A partir dessas informações, ele calcula automaticamente as correntes de cada fase e 
  do neutro, apresentando os resultados tanto em forma numérica quanto em um 
  <strong>diagrama fasorial interativo</strong>.
</p>

<h2>Funcionalidades Implementadas</h2>
<ul>
  <li>Interface gráfica desenvolvida em <strong>Tkinter</strong> para adição e gerenciamento de cargas.</li>
  <li>Cálculo automático das correntes de fase e corrente de neutro.</li>
  <li>Suporte a cargas monofásicas, bifásicas e trifásicas.</li>
  <li>Atualização dinâmica dos resultados conforme as cargas são modificadas.</li>
  <li>Geração de <strong>diagrama fasorial</strong> das correntes totais utilizando <strong>Matplotlib</strong>.</li>
  <li>Exibição das magnitudes e ângulos das correntes em forma polar.</li>
  <li>Funções para modificar e deletar cargas adicionadas.</li>
</ul>

<h2>Tecnologias Utilizadas</h2>
<ul>
  <li><strong>Python</strong> — linguagem de programação principal.</li>
  <li><strong>Tkinter</strong> — biblioteca para a interface gráfica.</li>
  <li><strong>Matplotlib</strong> — biblioteca para plotagem do diagrama fasorial.</li>
  <li><strong>Numpy</strong> — para cálculos matemáticos e conversões polares.</li>
</ul>

<h2>Próximos Passos</h2>
<ul>
  <li>Incluir fator de potência e cálculo de componentes reativas.</li>
  <li>Permitir exportar relatórios de cálculo em PDF ou Excel.</li>
  <li>Adicionar suporte a sistemas monofásicos de duas fases (127/220V).</li>
  <li>Melhorar a visualização do diagrama fasorial com escala automática e cores diferenciadas.</li>
</ul>
