import os  
import sys
import platform

from string import Template

def makeNode(index,start=0,shape='circle',num=3,height='.5'):
    code = Template('''
    node [shape=$shape,height=$height];\n
    $nodes;\n
    ''')
    node_set=[];
    nodes=''

    for i in range(num):
        n = 'a%d' %index + '%d' %(start+i)
        node_set.append(n)
        nodes = nodes + (n + ' ')
    
    str = code.substitute(index=index, shape=shape, nodes=nodes,height=height)
    return node_set,str

def makeLayer(index,color='red2',node_num=3, maxNum=2,name=''):
    code = Template('''subgraph cluster_$index {\n 
    color=white;\n
    node [style=solid,color=$color];\n
    $nodesB$nodesM$nodesE
    label = "layer $name($node_num)";\n
    }\n
    ''')
    nodesB=''
    nodesM=''
    nodesE=''
    node_set=[];
    if node_num > maxNum:
        headNum = maxNum // 2
        bset,nodesB = makeNode(index=index,num=headNum)
        _,nodesM = makeNode(index=index,start=headNum,shape='point',height='.02')
        eset,nodesE = makeNode(index=index,start=(node_num-headNum),num=headNum)
        node_set = (bset+eset)
    else:
        nodes,nodesM = makeNode(index=index,num=node_num)
        node_set = nodes
    if name=='':
        name = index
    str = code.substitute(index=index,name=name, color=color, nodesB=nodesB,nodesM=nodesM,nodesE=nodesE,node_num=node_num)
    return node_set,str

def makeLines(connects,node_sets):
    str=''
    for c in connects:
        for i1 in node_sets[c[0]]:
            for i2 in node_sets[c[1]]:
                str = str + (i1 + ' -> ' + i2) + '\n'
    return str;

def makeFrame(args):
    code = Template('''digraph G {\n 
    rankdir=LR\n
    splines=line\n
    nodesep=.05;\n
    node [label=""];\n
    $layers\n
    $lines\n
    } 
    ''')
    node_sets=[]
    layer_num = args["layers_num"]
    layers_cfg = args['layers_cfg']
    connects = args['connects']
    visual_num = args['visual_num']
    layers = '';
    for i in range(layer_num):
        node_set,str = makeLayer(i,layers_cfg[i][2],layers_cfg[i][1],visual_num,layers_cfg[i][0])
        node_sets.append(node_set)
        layers = layers + str
    
    lines = makeLines(connects,node_sets)
    return code.substitute(layers=layers,lines=lines)

def saveFile(str, path):  
    print (path)
    f = open(path,'w')  
    f.write(str)
    f.close()
    
def isWindowsSystem():
    return 'Windows' in platform.system() 

def makeConfig():
    args = sys.argv[1:]
    if len(args) == 0:
       args = makeDefConfig()
    else:      
        fp =  open(args[0],'r')
        args = dict()
        line = fp.readline();
        while line:
            if line.index('#') > 1:
                item = line.split(':')
                args.update({item[0]:item[1]})
        line = fp.readline()
    return args

def makeDefConfig():
    args = dict()
    #path
    path = sys.argv[0]
    if isWindowsSystem():
        last = path.rindex('\\')
    else:
        last = path.rindex('/')
    
    path = path[0:last+1]
    args.update({'input':path + 'nn.gv'})
    args.update({'output':path + 'nn.png'})
    #layer number
    args.update({'visual_num':2})
    #layers config:(name,nodes number,color)
    args.update({'layers_cfg':(('input',1,'blue4'),('h2',5,'red2'),('h3',5,'red2'),('h4',5,'red2'),('out',2,'seagreen2'))})
    layers = args['layers_cfg']
    args.update({'layers_num':len(layers)})
    #connects:layer_i->lay_j
    args.update({'connects':([0,1],[0,2],[0,3],[1,4],[2,4],[3,4])})
    return args

if __name__ == "__main__":
    args = makeConfig()
    
    str = makeFrame(args)
    saveFile(str, args['input'])
    cmd = 'dot ' + args['input'] + ' -Tpng -o ' + args['output']
    os.system(cmd)
