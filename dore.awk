BEGIN {
	anyo=0;
	mes=0;
	dia=0;
	reset();
	count=0;
	salto=" ";
	separador="\n"
}
function getMes(s) {
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
}
function cero(s) {
	if ((s+0)>9) return s;
	return "0" s;
}
function item() {
	if (hora!=0 && sala!=0 && nota!="" && minutos>0) {
		gsub(/^\s+|\s+$/, "", nota);
		sub(/^Sala ([0-9]+|Verano) */, "", nota);
		gsub(/^\s+|\s+$/, "", nota);
		gsub(/^\s*\n\s*/, "\n", nota);
		if (split(nota,a,separador)>0) {
			titulo=gensub(/^([^\(]+) *\(.*/, "\\1", "", a[1]);
			estreno=gensub(/^[^\)]+, ([0-9]+)\).*/, "\\1", "", a[1]);
			gsub(/\n+/, "\n  ", nota);
			gsub(/^\s+|\s+$/, "", titulo);
			gsub(/^\s+|\s+$/, "", nota);
			print "---"
			print "inicio: \"" anyo "-" cero(mes) "-" cero(dia) " " hora "\"";
			print "duración: \"" minutos "\"";
			print "sala: \"" sala "\"";
			print "título: \"" titulo "\"";
			#print estreno;
			print "nota: |"
			print "  " nota;
			print ""
		}
	}
	reset();
}
mes==0 && $1~/^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)$/ {
	mes=getMes($1);
}
anyo==0 && mes>0 && $1~/^[0-9][0-9][0-9][0-9]$/ {
	anyo=$1;
}

/^(Segunda proyección el día |Ver nota día )[0-9]+\.?$/ || /^Segunda proyección en /{
	item();
	getline
}

/^.?[0-9]+ - (Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)/ {
	dia=$1;
	sub(/[^0-9]+/, "", dia);
	item();
}
$1~/^[0-9]+:[0-9]+$/ {
	item();
	hora=$1;
}

nota!="" {
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

$NF~/^[0-9]+'$/ {
	minutos=substr($NF,0,length($NF)-1);
	if (nota!="") salto=separador;
}
$1~/^[0-2][0-9][0-6][0-9]$/ {
	_hora=gensub(/(..)(..)/, "\\1:\\2", "", $1);
}

END {
	item();
}
