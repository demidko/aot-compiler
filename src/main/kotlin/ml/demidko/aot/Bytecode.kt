package ml.demidko.aot

/**
 * Класс хранит константы байткода
 */
object Bytecode {
  const val endOfCompiledLine: Byte = 100
  fun isEndl(b: Byte): Boolean {
    return b == endOfCompiledLine
  }

  fun isContent(b: Byte): Boolean {
    return b != endOfCompiledLine
  }
}