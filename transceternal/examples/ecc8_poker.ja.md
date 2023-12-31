## 概要
（ここには限定的な情報しかないので @hiromi_mi さんによる[貴重な日本語資料](https://hiromi-mi.github.io/trans.pdf)を適宜参照されたい）
各ノードの出次数が2の有向グラフで表されたプログラムに対してグラフ書き換えを繰り返していく言語。入出力を含むデータも同じグラフ上に表現されていて命令とデータの区別はない。

各ノードから出る2つの弧は0,1の番号で区別される。01列（空も含む）で表されるアドレスという概念があり、インタプリタに自動挿入されるrootノードからアドレスに示された順に0,1の弧をたどってたどり着くノードと対応する（アドレスからノードへは一意に対応するが、ノードに対応するアドレスは複数ありうることに注意）。以下アドレスは`[]`で囲んで表し、アスキーアート上では縦方向を0の弧、横方向を1の弧とする。

グラフの構造は過去の解を参考に以下のようにした。

```
root - <input (current char head)>
|
0 - A (program)
|
1 - <current line head>
|
2 (read only, B0)
|
3 - <output (=input) head>
```

- `[1]`は入出力に使われるノードで、プログラム開始時にはインタプリタによって入力文字列がビット単位で連結リストのようにつながれている。また、プログラム終了時はここにつながったノードをビットとして解釈して出力が行われる。ここは文字を読むごとに8bitずつずらしていく（`[1]`に`[111111111]`をつなぎ変える）。
- `[01]`は次に実行する命令を表すノードで、ここから1方向に後に疑似コードで示す命令が連なる。
- `[001]`は言語仕様上`B1`と呼ばれるノードで、プログラム開始時に入力のビットが立っているところから弧が張られているほか、ノードを追加するadd命令かどうかの判定に使われる。ただし、今回はadd命令は使わず、入力についてもビットが0かどうかで区別するようにすることで、`B1`としての機能は使用しない。入力の行ごとの先頭を指した状態にして、先頭2文字をFやSに書き換えて出力する際に使用する。
- `[000]`は言語仕様上`B0`と呼ばれるノードで、プログラム開始時に入力のビットが落ちているところから弧が張られているほか、弧を張り替えるset命令かどうかの判定、プログラムの終了判定、出力ビットが0かどうかの判定に使われる。これはプログラム開始時から書き換えずに使う。ただし`000`より`0001`のほうが生成しやすいのでノード2の1側の弧は自己ループさせて`[0001]`で参照する。
- `[00001]`は入力の先頭を覚えておくのに使う。プログラム終了間際に`[1]`にコピーすることで、書き換え後の入力文字列を出力する。

## アルゴリズム・命令列
出力ビット列を構成するのは、既存のビット列につなぎ変えたり（Esolang wikiにあるサンプル）入力ビット列から部分的にコピーしてきたり（第6回の解）するほうが、add命令でノードを追加していくよりも楽だと考えられる。特に今回は無駄な文字を出してもよいことになっているので、入力文字列の一部ビットを書き換えた上でそのまま出してやるのが、構成中の出力文字列の終端を覚えておくノードが不要になるぶん得だと考えた。

入出力がビット単位で行われるので、フラッシュ・ストレート判定およびF・Sの生成は以下のようにした。
- フラッシュ
  1. あらかじめ行の先頭文字の4の位（下から3ビット目）を立てておく（疑似コードのw）
  2. 各スート文字について行の先頭文字の下位2ビットと比較し、不一致なら先頭文字の4の位を落とす（疑似コードのa～c）
  3. 行末まで来たら先頭文字の下位2ビットを0b10に書き換える（疑似コードのs, t）
- ストレート
  1. あらかじめ行の先頭から2文字目の8の位、16の位、128の位を反転させて0b10101xxxにしておく（疑似コードのx～z）
  2. 各数字文字について下位3ビットのの数値に対応するビットをSの文字コードのものに置き換える（疑似コードのe～m）
  3. 各数字文字について下位3ビットを0b011に書き換える（2.の判定後なので書き換えて問題ない）（疑似コードのn～p）

（後述するアドレス生成用の無駄命令だけ挿入した）比較的素直な疑似コードは以下のようになる。

```
A: set [00001] = [1]
B: if [0001] == [11110] ? v : C
C: set [1] = [00001]
D: (dummy if to generate 11...110; anyway goto 2 (end))
v: set [001] = [1]
w: set [1110] = []
x: set [11111111'11110] = []
y: set [11111111'111110] = [0001]
z: set [11111111'111111110] = []
a: if [0010] == [10] ? b : c
b: if [00110] == [110] ? E : c
c: set [001110] = [0001]
E: if [0001] == [11110] ? d : v (dummy if to generate 11...11; always taken)
d: set [1] = [11111111'1]
e: if [10] == [0001] ? f : g
f: if [110] == [0001] ? l : j
g: if [110] == [0001] ? h : k
h: if [1110] == [0001] ? i : m
i: set [00'11111111'11110] = [0001]; goto n
j: set [00'11111111'111110] = []; goto n
k: set [00'11111111'1111110] = [0001]; goto n
l: set [00'11111111'11111110] = []; goto n
m: set [00'11111111'111111110] = [0001]; goto n
n: set [10] = []
o: set [110] = []
p: set [1110] = [0001]
q: set [1] = [11111111'1]
r: if [0001] == [11110] ? a : s
s: set [0010] = [10]
t: set [00110] = [110]
u: set [1] = [11111111'1]; goto B
```

### ゴルフポイント1: ノードの共有
Transceternalではノードの数がプログラムのバイト数に直結する。基本的に命令数が減ればノード数は減るが、それ以外のテクニックを紹介する。

命令のグラフ構造は以下のようになっている。B2はB0でもB1でもない任意のノード、ドットで表されるノードは疑似コードに現れない中間ノードである。`{}`はアドレスとして解釈したときに所望の01列になるノードを表す。

```
(set)             (add)                  (if)
X - <next inst>   X - <next inst>        X - <not taken inst>
|                 |                      |
. - . - {src}     . - . --- . - {src1}   . - . - <taken inst>
|   |             |   |     |            |   |
B0  {dst}         B1  {dst} {src0}       B2  . - {addr1}
                                             |
                                             {addr0}
```

命令の引数のアドレスペア（addではsrcのペア）が同じものは、一つのアドレスペアを表すノードを共有できる。たとえば疑似コードのhとpは同じ`[1110]`と`[0001]`を使っているので同じノードを使い回すことができる。ここでsetはアドレス間に順序があるのに対してifはアドレスの入れ替えが可能であることに注意。後述するアドレス生成のことを忘れると（おそらく加味しても）使い回しで得をするように入れ替えてよい。

また、set命令についてはアドレスペアが同じもの同士で(B0, アドレスペア)のノード自体を共有できる。たとえば疑似コードに3回出てくる`set [1] = [11111111'1]`が該当する。ifについても、アドレスペアが同じでtakenの行き先が同じものはまとめられるが、今回はそのような場面がなかった。

原理的には、たとえばset命令の(`{dst}`, `{src}`)がif命令の(アドレスペアを表すノード, takenの行き先)と一致している場合でも同じノードを共有できる。こういった最適化については最後に補足する。

### ゴルフポイント2: アドレス
アドレスのエンコードは以下のようなグラフで行われる。（入出力文字列のエンコードも同じ）

```
(B0で終止するパターン)
X - . - . - . - ... - . - B0
|   |   |   |         |
b0  b1  b2  b3        bn

(visitedノードで終止するパターン)
X - . - Y - . - ... - . - Y
|   |   |   |         |
b0  b1  b2  b3        bn
```

ここで`b0`,`b1`,...はB0のとき0、それ以外のとき1を表す。つまり、ノードXが表現するアドレスは「1方向に辿っていってB0あるいは訪問済みのノードに到達するまでの、各ノードの0方向のノードがB0かどうか」になっている。

Xの1方向のノードをX[1]と表すと、B0で終止する場合やX以外のノードでvisited判定されて終止する場合は`addr(X) = (b0==B0?'0':'1') + addr(X[1])`の関係が成り立つ。アドレスペアを表すノードのことを思い出すと、
```
X - {addr1}
|
{addr0}
```
`{addr0}`がB0のときは'0'+addr1、それ以外のときは'1'+addr1がX自身の表現するアドレスとなる。ここで、B0が表すアドレスは''（空列）でrootノードに対応するが、addr0はsetのdst側だったりifの片側だったりして、rootノードを指定することは考えづらい（もちろん後述するとおりrootノードを触ることで短くなるケースはある）。つまりXが表すアドレスは'1'+addr1であると考えてよく、「set命令やif命令があればそれのsrcやaddr1の頭に'1'をつけたアドレスがタダで生える」ことになる。

さらに、set命令の場合はアドレスペアの手前に「setであることを表す0側がB0のノード」がついているので、「srcの頭に'01'をつけたアドレス」もタダで生成される。同様にif命令については「takenで遷移するノードが表すアドレスの頭に'11'をつけたアドレス」が生成される。

疑似コード中に出現する定数は`11...110`, `0011...110`, `11...11`, `00..001`の4パターンがある。前の2つは着目している文字が`1`に、着目している入力行が`001`につながっていることによる。ここで頭に1がつくアドレスのほうが生成しやすいことを考えると、どちらでも参照できる場合は`11...110`を使ったほうが得ということになる。（そもそも`0011...110`が`11...110`を含んでいるのであまり説得力のある例ではないが）

さて、ここまでの考察では既存のアドレスを1ビットずつ伸ばしていくことを考えていたが、コード中に都合よく1ビットずつ伸びていくアドレス群が現れるわけではなく、このままではアドレス生成のために追加されるノードが多くなってしまう。ここで`[01]`以降につながる命令のリストをアドレスとして利用することを考える。set命令の1側は後続の命令、if命令の1側はnot takenの命令につながっている。これらの命令の0側にはset命令やif命令であることを表すための中間ノードがつながっており、（意図しないかぎりB0ではないので）アドレスビットとして解釈すると1である。

上の疑似コードでD,Eのif命令がない（Cのset命令から2へ遷移し終了する）状態を考える。vのset命令から1側の弧をたどってB0にたどりつくまでの接続は以下のとおりで、21ビット1が連続するアドレスを表している。
```
v - w - x - y - z - a - c - d - e - g - k - n - o - p - q - r - s - t - u - B - C - 2
```
（なおvをtakenに持つBのif命令の中間ノードの表現するアドレスが23ビット連続の1で最長となる）

1が連続するだけのアドレスは`11111111'1`で十分で、むしろ今一番欲しいものは`11111111'111111110`なので、最後に0をつけ足したい。そこでまず、Cの後ろに0側にB0を持つノードDをつなぐことを考える。

```
D - 2     D - 2
|         |
2      =  2 - 2 - 2
          |   |
          3   3 - <output head>
              |
              3
```

今回のB0であるノード2は0側にノード3、1側は自己ループでノード2がつながっている。これによりノードDはif命令と解釈され、not taken側に2をつなぐと、takenでもnot takenでも2に遷移する便利なノードとなる。

これで`11...110`は手に入るようになったが、次は`11...11`がなくなってしまったので、これを復活させる。これは、なんでもないところに常にtakenになるif命令を挟んで、not taken側をループさせたりB0につないだりしてやれば実現できる。これがEのif命令である。`11...110`の最大長が短くなってしまうが、今回はコードの長さが十分あって、`11111111'111111110`も`11111111'1`も手に入った。

### ゴルフポイント3: 終止方法の見直し
入力がなくなったときに出力の先頭`[00001]`を`[1]`にコピーして終了していたが、これを「rootノードを`[10]`で置き換える」とする（入力がなくなると`[1]`にはB0がつながっているので、`[101]`に出力の先頭があることに注意）。rootを置き換えるとB0や命令列が置き換わってしまって破滅するリスクがあるが、初期状態で`[00000]`に（自己ループでなく）B0をつないでおくと、下に示すようにうまい具合にB0はそのまま、命令は終止という状態にできる（気持ちいい）。

```
root - 2                3 - <output head>
|                       |
0 - C - D - 2           2 - 2
|                       |
1 - <last line head> -> 3 - <output head> = B1
|                       |
2                       2 = B0
|
3 - <output head>
|
2
|
...
```

B0の1側が自己ループになっていることから、rootを置き換えるノードのアドレスは好きな長さの11...110としてよい。set命令の構造は以下のようになって頭に00がついたアドレスが自動で生える。Cの命令自身をアドレスペアとして解釈すると、`[0011...110]`に`[0]`をコピーするset命令に使えることから、`j: set [00'11111111'111110] = []`でこれを使うことにする（代入するものはB0でなければ何でもよいので）。

```
C - D - 2               C - {0}
|                       |
. - . - {11...110}  =   {0011...110}
|   |
B0  {}=B0
```

なおプログラム開始時点で`[0100]`にB0がつながっている（＝先頭の命令がset）ことを利用すると`A: set [00001] = [1]`は`A: set [010001] = [1]`とすることができ、これによって`[00001]`は一切プログラムに登場しないようにできる。（`{010001}`は`[0001]`をsetする命令のところに自動的に生える）

### ゴルフポイント4: ノード共有再び
疑似コードで表現された命令列からグラフを構築すると、「if命令であることを示すB0でもB1でもないノード」（仮にB2としている）以外の全てのノードについて、そのノードが表現するアドレスを計算することができる（命令の動的書き換えを行わない前提）。それを元に疑似コードに現れない中間ノードを他の中間ノードや命令のノードと共有することを考える。

まずアドレスペアノードについては、単純に0側のノードが表すアドレスと1側のノードが表すアドレスがそれぞれaddr0, addr1と一致するようなノードを探せばよい。ただしこのとき、0側にB2がぶら下がっている箇所（つまりifの中間ノード）に関してはB2として`{addr0}`を採用すればよいのでif命令を書き換えてノードを共有するようにする。また、`{addr1}`が「B0以外のノード」で十分な場合はプログラムが噓解法にならない範囲で都合のよいアドレスに書き換えて共有する。

また、ifの中間ノードに関しては、taken側の命令を2つ先に持つ命令で丸ごと置き換え可能となる場合がある。今回は`B: if [0001] == [11110] ? v : C`の中間ノード（下図の`*`で示すノード）を`c: set [001110] = [0001]`で置き換える。このとき、cの後続の`E: if [0001] == [11110] ? d : v`のB2が`{addr0}`、dが表すアドレスの頭に1をつけたものが`{addr1}`となるので、EのB2を`{0001}`に、Bを`if [0001] == [11111111'11111110]`に書き換える。（入力終端以外では数字の64の位なのでB0、入力終端ではB0の0側のノード=非B0となる）

```
B                               c - E - v
|                               |   |
* - . - v                       .   . - . - d = {11111111'1111110}
|   |                               |   |
B2  . - {11111111'11111110}         B2  . - {11111111'11111110}
    |                                   |
    {0001}                              {0001}
```

これらのノード共有を考慮した最終的な疑似コードは以下のようになる。

```
A: set [010001] = [1]
B: if [0001] == [11111111'11111110] ? v : C
C: set [] = [11111111'111110]
D: (dummy if to generate 11...110; anyway goto 2 (end))
v: set [001] = [1]
w: set [1110] = [11111111]
x: set [11111111'111110] = [11111111'11110]
y: set [11111111'11110] = []
z: set [11111111'111111110] = [11111111]
a: if<00'11111111'11111110> [0010] == [10] ? b : c
b: if<1> [00110] == [110] ? E : c
c: set [001110] = [11111111'11110]
E: if<0001> [0001] == [11111111'11111110] ? d : v (dummy if to generate 11...11; always taken)
d: set [1] = [11111111'1]
e: if<00'11111111'11110> [10] == [0001] ? f : g
f: if<11111111'111110> [110] == [0001] ? l : j
g: if<00'11111111'1111110> [110] == [0001] ? h : k
h: if<001110> [1110] == [0001] ? i : m
i: set [00'11111111'11110] = [11111111'111110]; goto n
j: set [00'11111111'111110] = [0]; goto n
k: set [00'11111111'1111110] = [11111111'111110]; goto n
l: set [00'11111111'11111110] = [11111111'11]; goto n
m: set [00'11111111'111111110] = [11111111'1111110]; goto n
n: set [10] = [11111111'1]
o: set [110] = [11111111'1]
p: set [1110] = [0001]
q: set [1] = [11111111'1]
r: if<10> [0001] == [11111111'11111110] ? a : s
s: set [001] = [10]
t: set [00110] = [110]
u: set [1] = [11111111'1]; goto B
```

これをアセンブルすると181Bのコードが得られる。
