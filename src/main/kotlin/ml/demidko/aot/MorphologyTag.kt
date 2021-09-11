package ml.demidko.aot

/**
 * В этом перечислении ни в коем случае нельзя менять порядок элементов.
 * От этого зависит корректность компиляции и декомпиляции.
 * @see <a href="http://phpmorphy.sourceforge.net/dokuwiki/manual-graminfo">Расшифровка аббревиатур</a>
 */
enum class MorphologyTag(private val token: String) {
  Plural("мн"),
  Male("мр"),
  Nominative("им"),
  Pronoun("МС"),
  Abbreviation("аббр"),
  ShortAdjective("КР_ПРИЛ"),
  Comparative("сравн"),
  Dative("дт"),
  PresentTense("нст"),
  IndicativeAdverb("указат"),
  PerfectVerb("св"),
  MiddleName("отч"),
  Verb("Г"),
  PastTime("прш"),
  Interjection("МЕЖД"),
  Adverb("Н"),
  Singular("ед"),
  NeuterGender("ср"),
  Adjective("П"),
  Noun("С"),
  Inanimate("но"),
  Organization("орг"),
  Introduction("ВВОДН"),
  Transitive("нп"),
  Imperfect("нс"),
  Archaism("арх"),
  Toponym("лок"),
  MaleFemale("мр-жр"),
  PronounPredicative("МС-ПРЕДК"),
  FirstPerson("1л"),
  ImpersonalVerb2("*"),
  PassiveParticiple("стр"),
  Ablative("тв"),
  Immutable("0"),
  SecondGenetive("2"),
  ColloquialSpeech("разг"),
  Animated("од"),
  Typo("опч"),
  PronounAdjective("МС-П"),
  Participle("ПРИЧАСТИЕ"),
  SuperlativeAdjective("прев"),
  Surname("фам"),
  QualitativeAdjective("кач"),
  ActiveVoice("дст"),
  VerbalParticiple("ДЕЕПРИЧАСТИЕ"),
  BreifComunion("КР_ПРИЧАСТИЕ"),
  AdjectiveUnusedType("дфст"),
  SecondPerson("2л"),
  Female("жр"),
  Accusative("вн"),
  FutureTime("буд"),
  InterrogativeAdverb("вопр"),
  POSL_PART_OF_SPEECH("ПОСЛ"),
  Intransive("пе"),
  Slang("жарг"),
  Imperative("пвл"),
  Numeral("ЧИСЛ"),
  Predicative("ПРЕДК"),
  Particle("ЧАСТ"),
  Pretext("ПРЕДЛ"),
  Vocative("зв"),
  Name("имя"),
  Prepositional("пр"),
  ThirdPerson("3л"),
  Infinitive("ИНФИНИТИВ"),
  InpersonalVerb("безл"),
  Superlative("притяж"),
  OrdinalNumber("ЧИСЛ-П"),
  Idiom("ФРАЗ"),
  Genitive("рд"),
  Union("СОЮЗ");

  override fun toString(): String {
    return token
  }

  companion object {
    fun fromString(token: String): MorphologyTag {
      for (info in values()) {
        if (info.token == token) {
          return info
        }
      }
      throw IllegalArgumentException("Invalid token: $token")
    }
  }
}

/*
Расшифровка аббревиатур используемых в этом перечислении (!)

Части речи
дескриптор 	константа пример 	описание
C 	PMY_RP_NOUN 	мама 	существительное
П 	PMY_RP_ADJ_FULL 	красный 	прилагательное
КР_ПРИЛ 	PMY_RP_ADJ_SHORT 	красива 	краткое прилагательное
ИНФИНИТИВ 	PMY_RP_INFINITIVE 	идти 	инфинитив
Г 	PMY_RP_VERB 	идет 	глагол в личной форме
ДЕЕПРИЧАСТИЕ 	PMY_RP_ADVERB_PARTICIPLE 	идя 	деепричастие
ПРИЧАСТИЕ 	PMY_RP_PARTICIPLE 	идущий 	причастие
КР_ПРИЧАСТИЕ 	PMY_RP_PARTICIPLE_SHORT 	построена 	краткое причастие
ЧИСЛ 	PMY_RP_NUMERAL 	восемь 	числительное (количественное)
ЧИСЛ-П 	PMY_RP_NUMERAL_P 	восьмой 	порядковое числительное
МС 	PMY_RP_PRONOUN 	он 	местоимение-существительное
МС-ПРЕДК 	PMY_RP_PRONOUN_PREDK 	нечего 	местоимение-предикатив
МС-П 	PMY_RP_PRONOUN_P 	всякий 	местоименное прилагательное
Н 	PMY_RP_ADV 	круто 	наречие
ПРЕДК 	PMY_RP_PREDK 	интересно 	предикатив
ПРЕДЛ 	PMY_RP_PREP 	под 	предлог
СОЮЗ 	PMY_RP_CONJ 	и 	союз
МЕЖД 	PMY_RP_INTERJ 	ой 	междометие
ЧАСТ 	PMY_RP_PARTICLE 	же, бы 	частица
ВВОДН 	PMY_RP_INP 	конечно 	вводное слово
ФРАЗ 	PMY_RP_PHRASE 	бухты-барахты, зги 	фразеологизм

Граммемы
граммема 	константа описание

Род
мр 	PMY_RG_MASCULINUM 	мужской род
жр 	PMY_RG_FEMINUM 	женский род
ср 	PMY_RG_NEUTRUM 	средний род
мр-жр 	PMY_RG_MASC_FEM 	общий род (сирота, пьяница)

Число
ед 	PMY_RG_SINGULAR 	единственное число
мн 	PMY_RG_PLURAL 	множественное число

Падеж
им 	PMY_RG_NOMINATIV 	именительный
рд 	PMY_RG_GENITIV 	родительный
дт 	PMY_RG_DATIV 	дательный
вн 	PMY_RG_ACCUSATIV 	винительный
тв 	PMY_RG_INSTRUMENTALIS 	творительный
пр 	PMY_RG_LOCATIV 	предложный
зв 	PMY_RG_VOCATIV 	звательный (отче, боже)
2 	PMY_RG_SECOND_CASE 	второй родительный или второй предложный падежи

Время
нст 	PMY_RG_PRESENT_TENSE 	настоящее время
буд 	PMY_RG_FUTURE_TENSE 	будущее время
прш 	PMY_RG_PAST_TENSE 	прошедшее время

Лицо
1л 	PMY_RG_FIRST_PERSON 	первое лицо
2л 	PMY_RG_SECOND_PERSON 	второе лицо
3л 	PMY_RG_THIRD_PERSON 	третье лицо

Одушевленность
од 	PMY_RG_ANIMATIVE 	одушевленное
но 	PMY_RG_NON_ANIMATIVE 	неодушевленное

Вид
св 	PMY_RG_PERFECTIVE 	совершенный вид
нс 	PMY_RG_NON_PERFECTIVE 	несовершенный вид

Переходность
нп 	PMY_RG_NON_TRANSITIVE 	переходный
пе 	PMY_RG_TRANSITIVE 	непереходный

Залог
дст 	PMY_RG_ACTIVE_VOICE 	действительный залог
стр 	PMY_RG_PASSIVE_VOICE 	страдательный залог

Другое
0 	PMY_RG_INDECLINABLE 	неизменяемое
безл 	PMY_RG_IMPERSONAL 	безличный глагол
пвл 	PMY_RG_IMPERATIVE 	повелительное наклонение (императив)
притяж 	PMY_RG_POSSESSIVE 	притяжательное (не используется)
прев 	PMY_RG_SUPERLATIVE 	превосходная степень (для прилагательных)
сравн 	PMY_RG_COMPARATIVE 	сравнительная степень (для прилагательных)
кач 	PMY_RG_QUALITATIVE 	качественное прилагательное
дфст 	PMY_RG_DE_FACTO_SING_TANTUM 	??? прилагательное (не используется)

Семантические признаки
имя 	PMY_RG_NAME 	имя (Иван, Михаил)
фам 	PMY_RG_SUR_NAME 	фамилия (Иванов, Сидоров)
отч 	PMY_RG_PATRONYMIC 	отчество (Иванович, Михайлович)
лок 	PMY_RG_TOPONYM 	топоним (Москва, Лена, Эверест)
аббр 	PMY_RG_INITIALISM 	аббревиатура (КПСС, РОНО)
орг 	PMY_RG_ORGANISATION 	организация
вопр 	PMY_RG_INTERROGATIVE 	вопросительное наречие
указат 	PMY_RG_DEMONSTRATIVE 	указательное наречие
жарг 	PMY_RG_SLANG 	жаргонизм
разг 	PMY_RG_COLLOQUIAL 	разговорный
арх 	PMY_RG_ARCHAISM 	архаизм
опч 	PMY_RG_MISPRINT 	опечатка
поэт 	PMY_RG_POETRY 	поэтическое
проф 	PMY_RG_PROFESSION 	профессионализм
полож 	PMY_RG_POSITIVE 	??? (не используется)
*/