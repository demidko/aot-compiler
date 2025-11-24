package ml.demidko.aot

import com.github.demidko.aot.bytecode.MorphologyTag
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets


/**
 * Класс считывает из ресурсов набор лемм
 */
internal object LemmasReader {
  private fun bufferedReaderOfResource(resourceName: String): BufferedReader {
    return BufferedReader(
      InputStreamReader(
        LemmasReader::class.java.getResourceAsStream(resourceName),
        StandardCharsets.UTF_8
      )
    )
  }

  @Throws(IOException::class)
  private fun readGramtabLine(reader: BufferedReader): String? {
    val line = reader.readLine() ?: return null
    // отбрасываем комментарии и пустые строки
    return if (line.isEmpty() || line.startsWith("//")) {
      readGramtabLine(reader)
    } else line
  }

  @Throws(IOException::class)
  private fun readMorphology(): Map<String, List<MorphologyTag>> {
    val result = mutableMapOf<String, List<MorphologyTag>>()
    bufferedReaderOfResource("/tab").use { reader ->
      var line = readGramtabLine(reader)
      while (line != null) {
        result[line.substring(0, 2)] =
          line.substring(5).split('[', ' ', ',', ']').filterNot(String::isEmpty).map(MorphologyTag::fromString)
        line = readGramtabLine(reader)
      }
    }
    return result
  }

  @Throws(IOException::class)
  private fun readInt(reader: BufferedReader): Int {
    return reader.readLine().toInt()
  }

  @Throws(IOException::class)
  private fun skipLines(reader: BufferedReader, count: Int) {
    for (i in 0 until count) {
      reader.readLine()
    }
  }

  @Throws(IOException::class)
  private fun skipSection(reader: BufferedReader) {
    skipLines(reader, readInt(reader))
  }

  @Throws(IOException::class)
  private fun readParadigmsSection(reader: BufferedReader): List<String> {
    val result = ArrayList<String>()
    val len = readInt(reader)
    for (i in 0 until len) {
      result.add(reader.readLine())
    }
    return result
  }

  @Throws(IOException::class)
  fun readLemmas(): List<List<FullFlexion>> {
    val result = ArrayList<List<FullFlexion>>()
    val morphMap = readMorphology()
    bufferedReaderOfResource("/mrd").use { reader ->
      val paradigms = readParadigmsSection(reader)
      skipSection(reader)
      skipSection(reader)
      skipSection(reader)
      val len = readInt(reader)
      for (i in 0 until len) {
        val line = reader.readLine()
        // фильтр метапостфиксов
        if (line.startsWith("-")) {
          continue
        }
        val tokens = line.split(" ").toTypedArray()
        result.add(FlexionFabric.createLemma(tokens[0], paradigms[tokens[1].toInt()], tokens[4], morphMap))
      }
    }
    return result
  }
}
