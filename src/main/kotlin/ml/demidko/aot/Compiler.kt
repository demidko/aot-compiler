package ml.demidko.aot

import com.github.demidko.aot.bytecode.Bytecode.endOfCompiledLine
import com.github.demidko.aot.bytecode.MorphologyTag
import com.github.demidko.aot.bytecode.Utils.safeCharToByte
import ml.demidko.aot.Hashes.calculate
import ml.demidko.aot.LemmasReader.readLemmas
import ml.demidko.aot.Zip.zip
import java.io.DataOutputStream
import java.io.FileOutputStream
import java.io.IOException
import java.io.UncheckedIOException
import java.util.*
import java.util.zip.GZIPOutputStream

object Compiler {

  @Throws(IOException::class)
  @JvmStatic
  fun main(args: Array<String>) {
    println("Reading...")
    val zippedLemmas = zip(readLemmas())
    println("Compilation [1..4]")
    DataOutputStream(GZIPOutputStream(FileOutputStream("mrd.gz"))).use { file ->
      println("1. Morphology (" + zippedLemmas.morph.size + ")")
      compileMorphology(file, zippedLemmas.morph)
      println("2. Strings (" + zippedLemmas.strings.size + ")")
      compileStrings(file, zippedLemmas.strings)
      println("3. Lemma indexes (" + zippedLemmas.lemmas.size + ")")
      compileLemmas(file, zippedLemmas.lemmas)
      val hashes: Map<Int, Set<Int>> = calculate(zippedLemmas)
      println("4. Flexion hashes (" + hashes.size + ")")
      compileHashes(file, hashes)
    }
    println("Mrd-file successfully compiled to mrd.gz")
  }

  // 1
  @Throws(IOException::class)
  private fun compileMorphology(file: DataOutputStream, morph: List<Set<MorphologyTag>>) {
    file.writeInt(morph.size)
    var sizeInBytes = 0
    for (m in morph) {
      sizeInBytes += m.size
      sizeInBytes += 1
    }
    file.writeInt(sizeInBytes)
    for (m in morph) {
      file.write(bytesFromMorphology(m))
    }
  }

  @Throws(UncheckedIOException::class)
  private fun bytesFromMorphology(line: Set<MorphologyTag>): ByteArray {
    if (MorphologyTag.values().size >= endOfCompiledLine) {
      throw UncheckedIOException(IOException("GrammarInfo.values() >= " + endOfCompiledLine))
    }
    val res = ByteArray(line.size + 1)
    var resIndex = -1
    for (m in line) {
      res[++resIndex] = Arrays.binarySearch(MorphologyTag.values(), m).toByte()
    }
    res[line.size] = byteFromChar('\n')
    return res
  }

  private fun byteFromChar(n: Char): Byte {
    return if (n == '\n') endOfCompiledLine else safeCharToByte(n)
  }

  // 2
  @Throws(IOException::class)
  private fun compileStrings(file: DataOutputStream, strings: List<String>) {
    file.writeInt(strings.size)
    var sizeInBytes = 0
    for (s in strings) {
      sizeInBytes += s.length
      sizeInBytes += 1
    }
    file.writeInt(sizeInBytes)
    for (str in strings) {
      file.write(bytesFromString(str))
    }
  }

  private fun bytesFromString(s: String): ByteArray {
    val res = ByteArray(s.length + 1)
    for (i in 0 until res.size - 1) {
      res[i] = byteFromChar(s[i])
    }
    res[s.length] = byteFromChar('\n')
    return res
  }

  // 3
  @Throws(IOException::class)
  private fun compileLemmas(file: DataOutputStream, lst: List<List<MiniFlexion>>) {
    file.writeInt(lst.size)
    var sizeInBytes = 0
    for (l in lst) {
      sizeInBytes += 4
      for (f in l) {
        sizeInBytes += 8
      }
    }
    file.writeInt(sizeInBytes)
    for (lemma in lst) {
      file.writeInt(lemma.size)
      for (flexion in lemma) {
        file.writeInt(flexion.stringIndex)
        file.writeInt(flexion.morphIndex)
      }
    }
  }

  // 4
  @Throws(IOException::class)
  private fun compileHashes(file: DataOutputStream, hashes: Map<Int, Set<Int>>) {
    file.writeInt(hashes.size)
    var sizeInBytes = 0
    for ((_, value) in hashes) {
      // хеш
      sizeInBytes += 4
      // кол-во индексов
      sizeInBytes += 4
      // сами индексы
      sizeInBytes += value.size * 4
    }
    file.writeInt(sizeInBytes)
    for ((key, value) in hashes) {
      // хеш
      file.writeInt(key)
      // кол-во индексов
      file.writeInt(value.size)
      // индексы
      for (index in value) {
        file.writeInt(index)
      }
    }
  }
}