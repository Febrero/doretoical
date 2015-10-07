BEGIN {
#	IGNORECASE=1
	anyo=0;
	mes=0;
	dia=0;
	reset();
	count=0;
	salto=" ";
	separador="\n"
	pro=0;
	_mes=0;
}
function getMes(s) {
	gsub(/^\s+|\s+$/, "", s);
	s=tolower(s)
	if (s=="enero") return 1;
	if (s=="febrero") return 2;
	if (s=="marzo") return 3;
	if (s=="abril") return 4;
	if (s=="mayo") return 5;
	if (s=="junio") return 6;
	if (s=="julio") return 7;
	if (s=="agosto") return 8;
	if (s=="septiembre") return 9;
	if (s=="octubre") return 10;
	if (s=="noviembre") return 11;
	if (s=="diciembre") return 12;
}
function reset() {
	hora=0;
	sala=0;
	mimutos=0;
	nota="";
	_hora=0;
	buscadia=0;
}
function cero(s) {
	if ((s+0)>9) return s;
	return "0" s;
}
function escape(s) {
	gsub(/"/, "\\\"", s);
	return s
}
function item() {
	if (buscadia==1) return
	if (hora!=0 && sala!=0 && nota!="" && minutos>0) {
		gsub(/[ \t]+/, " ", nota);
		gsub(/^\s+|\s+$/, "", nota);
		sub(/^Sala ([0-9]+|Verano)\s*/, "", nota);
		gsub(/^\s*\n\s*/, "\n", nota);
		if (split(nota,a,separador)>0) {
			titulo=gensub(/^([^\(]+) *\(.*/, "\\1", "", a[1]);
			estreno=gensub(/^[^\)]+, ([0-9]+)\).*/, "\\1", "", a[1]);
			gsub(/^\s+|\s+$/, "", titulo);
			gsub(/\s+/, " ", titulo);
			gsub(/^\s+|\s+$/, "", nota);
			print "---"
			print "inicio: \"" anyo "-" cero(mes) "-" cero(dia) " " hora "\"";
			print "duración: \"" minutos "\"";
			print "sala: \"" sala "\"";
			print "título: \"" escape(titulo) "\"";
			#print estreno;
			if (nota=="") print "nota: \"\"";
			else {
				gsub(/\n+/, "\n  ", nota);
				print "nota: |"
				print "  " nota;
			}
		}
	}
	reset();
}

function programa() {
	print "---"
	print "programa: \"" anyo "-" cero(mes) "\"";
	print "fuente: \"" url "\"";
	next;
}

/^\s*$/ {
	next;
}
pro==0 && /^PROGRAMACIÓN$/ {
	pro=1;
	next;
}
pro==1 && mes==0 && anyo==0 && $NF~/^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)$/ {
	_mes=getMes($NF);
	pro=2;
}
pro==2 && mes==0 && anyo==0 && $0~/[0-9][0-9][0-9][0-9]/ {
	mes=_mes;
	anyo=$0;
	pro=3;
	programa();
}

/^<title>(Copia de )?[Cc]ara ?2/ || /^<title>ESTRELLA DE ORO/{
	print "---"
	print "error: wrong pdf format"
	exit 1
}

/^Premios Goya$/ {
	next
}

mes==0 && anyo==0 && $0~/^\s*(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE) [0-9][0-9][0-9][0-9]$/ {
	mes=getMes($1);
	anyo=$2;
	programa();
}

mes==0 && $1~/^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)$/ {
	mes=getMes($1);
}

anyo==0 && mes>0 && $1~/^[0-9][0-9][0-9][0-9]$/ {
	anyo=$1;
	programa();
}

/^(Segunda proyección el día|Ver nota día|Segunda proyección y nota día) [0-9]+\.?$/ || /^Segunda proyección en /{
	item();
	next;
}

NF==1 && $1~/^\s*(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)$/ {
	while (getline && $0~/^\s*$/) {
	
	}
	_d=$0
	sub(/^\s+|\s+$/, "", d);
	if (_d ~ /^[0-9]+$/) {
		item();
		dia=_d;
		next
	}
	buscadia=1;
}
buscadia==1 && NF==1 && $1~/^[0-9]+$/ {
	if ($0>0 && $0<32) {
		dia=$0;
		buscadia=0
		next
	}
}

/^\s*(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)[ \t]+[0-9]+\s*$/ {
	item();
	dia=$2;
	next
}
/^\s*[0-9]+ - (Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)/ {
	item();
	dia=$1;
	sub(/[^0-9]+/, "", dia);
	next
}
$1~/^[0-9]+(:|\.)[0-9]+$/ {
	item();
	hora=$1;
	sub(/\./, ":", hora);
	if (length(hora)==6) hora=substr(hora,0,5)
	if (hora=="24:00") hora="23:59"
}

buscadia==0 && nota!="" {
	nt=$0;
	gsub(/\s+/, " ", nt);
	gsub(/^\s+|\s+$/, "", nt);
	nota = (nota salto nt);
	salto=" ";
}

/^Sala ([0-9]+|Verano)/ {
	if (hora==0 && _hora!=0) {
		hora=_hora;
		_hora=0;
	}
	sala=$2;
	nota=$0;
}

$NF~/^[0-9]+['’]$/ {
	minutos=substr($NF,0,length($NF)-1);
	if (nota!="") salto=separador;
}
$1~/^[0-2][0-9][0-6][0-9]$/ {
	_hora=gensub(/(..)(..)/, "\\1:\\2", "", $1);
}

END {
	item();
}

