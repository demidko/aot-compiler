package ml.demidko.aot

internal object Utils {
  fun safeByteToChar(b: Byte): Char {
    val c = byteToChar(b)
    require(c.code != 0) { "Invalid byte character: $b" }
    return c
  }

  fun byteToChar(b: Byte): Char {
    return when (b) {
      0x2d.toByte() -> '-'
      0x96.toByte() -> '–'
      0x97.toByte() -> '—'
      0x30.toByte() -> '0'
      0x31.toByte() -> '1'
      0x32.toByte() -> '2'
      0x33.toByte() -> '3'
      0x34.toByte() -> '4'
      0x35.toByte() -> '5'
      0x36.toByte() -> '6'
      0x37.toByte() -> '7'
      0x38.toByte() -> '8'
      0x39.toByte() -> '9'
      0xa8.toByte() -> 'Ё'
      0xb8.toByte() -> 'ё'
      0xc0.toByte() -> 'А'
      0xc1.toByte() -> 'Б'
      0xc2.toByte() -> 'В'
      0xc3.toByte() -> 'Г'
      0xc4.toByte() -> 'Д'
      0xc5.toByte() -> 'Е'
      0xc6.toByte() -> 'Ж'
      0xc7.toByte() -> 'З'
      0xc8.toByte() -> 'И'
      0xc9.toByte() -> 'Й'
      0xca.toByte() -> 'К'
      0xcb.toByte() -> 'Л'
      0xcc.toByte() -> 'М'
      0xcd.toByte() -> 'Н'
      0xce.toByte() -> 'О'
      0xcf.toByte() -> 'П'
      0xd0.toByte() -> 'Р'
      0xd1.toByte() -> 'С'
      0xd2.toByte() -> 'Т'
      0xd3.toByte() -> 'У'
      0xd4.toByte() -> 'Ф'
      0xd5.toByte() -> 'Х'
      0xd6.toByte() -> 'Ц'
      0xd7.toByte() -> 'Ч'
      0xd8.toByte() -> 'Ш'
      0xd9.toByte() -> 'Щ'
      0xda.toByte() -> 'Ъ'
      0xdb.toByte() -> 'Ы'
      0xdc.toByte() -> 'Ь'
      0xdd.toByte() -> 'Э'
      0xde.toByte() -> 'Ю'
      0xdf.toByte() -> 'Я'
      0xe0.toByte() -> 'а'
      0xe1.toByte() -> 'б'
      0xe2.toByte() -> 'в'
      0xe3.toByte() -> 'г'
      0xe4.toByte() -> 'д'
      0xe5.toByte() -> 'е'
      0xe6.toByte() -> 'ж'
      0xe7.toByte() -> 'з'
      0xe8.toByte() -> 'и'
      0xe9.toByte() -> 'й'
      0xea.toByte() -> 'к'
      0xeb.toByte() -> 'л'
      0xec.toByte() -> 'м'
      0xed.toByte() -> 'н'
      0xee.toByte() -> 'о'
      0xef.toByte() -> 'п'
      0xf0.toByte() -> 'р'
      0xf1.toByte() -> 'с'
      0xf2.toByte() -> 'т'
      0xf3.toByte() -> 'у'
      0xf4.toByte() -> 'ф'
      0xf5.toByte() -> 'х'
      0xf6.toByte() -> 'ц'
      0xf7.toByte() -> 'ч'
      0xf8.toByte() -> 'ш'
      0xf9.toByte() -> 'щ'
      0xfa.toByte() -> 'ъ'
      0xfb.toByte() -> 'ы'
      0xfc.toByte() -> 'ь'
      0xfd.toByte() -> 'э'
      0xfe.toByte() -> 'ю'
      0xff.toByte() -> 'я'
      else -> Char(0)
    }
  }

  fun safeCharToByte(n: Char): Byte {
    val b = charToByte(n)
    require(b.toInt() != 0) { "Invalid character: $n" }
    return b
  }

  fun charToByte(n: Char): Byte {
    return when (n) {
      '-' -> 0x2d.toByte()
      '0' -> 0x30.toByte()
      '1' -> 0x31.toByte()
      '2' -> 0x32.toByte()
      '3' -> 0x33.toByte()
      '4' -> 0x34.toByte()
      '5' -> 0x35.toByte()
      '6' -> 0x36.toByte()
      '7' -> 0x37.toByte()
      '8' -> 0x38.toByte()
      '9' -> 0x39.toByte()
      '–' -> 0x96.toByte()
      '—' -> 0x97.toByte()
      'А' -> 0xc0.toByte()
      'Б' -> 0xc1.toByte()
      'В' -> 0xc2.toByte()
      'Г' -> 0xc3.toByte()
      'Д' -> 0xc4.toByte()
      'Е', 'Ё' -> 0xc5.toByte()
      'Ж' -> 0xc6.toByte()
      'З' -> 0xc7.toByte()
      'И' -> 0xc8.toByte()
      'Й' -> 0xc9.toByte()
      'К' -> 0xca.toByte()
      'Л' -> 0xcb.toByte()
      'М' -> 0xcc.toByte()
      'Н' -> 0xcd.toByte()
      'О' -> 0xce.toByte()
      'П' -> 0xcf.toByte()
      'Р' -> 0xd0.toByte()
      'С' -> 0xd1.toByte()
      'Т' -> 0xd2.toByte()
      'У' -> 0xd3.toByte()
      'Ф' -> 0xd4.toByte()
      'Х' -> 0xd5.toByte()
      'Ц' -> 0xd6.toByte()
      'Ч' -> 0xd7.toByte()
      'Ш' -> 0xd8.toByte()
      'Щ' -> 0xd9.toByte()
      'Ъ' -> 0xda.toByte()
      'Ы' -> 0xdb.toByte()
      'Ь' -> 0xdc.toByte()
      'Э' -> 0xdd.toByte()
      'Ю' -> 0xde.toByte()
      'Я' -> 0xdf.toByte()
      'а' -> 0xe0.toByte()
      'б' -> 0xe1.toByte()
      'в' -> 0xe2.toByte()
      'г' -> 0xe3.toByte()
      'д' -> 0xe4.toByte()
      'е', 'ё' -> 0xe5.toByte()
      'ж' -> 0xe6.toByte()
      'з' -> 0xe7.toByte()
      'и' -> 0xe8.toByte()
      'й' -> 0xe9.toByte()
      'к' -> 0xea.toByte()
      'л' -> 0xeb.toByte()
      'м' -> 0xec.toByte()
      'н' -> 0xed.toByte()
      'о' -> 0xee.toByte()
      'п' -> 0xef.toByte()
      'р' -> 0xf0.toByte()
      'с' -> 0xf1.toByte()
      'т' -> 0xf2.toByte()
      'у' -> 0xf3.toByte()
      'ф' -> 0xf4.toByte()
      'х' -> 0xf5.toByte()
      'ц' -> 0xf6.toByte()
      'ч' -> 0xf7.toByte()
      'ш' -> 0xf8.toByte()
      'щ' -> 0xf9.toByte()
      'ъ' -> 0xfa.toByte()
      'ы' -> 0xfb.toByte()
      'ь' -> 0xfc.toByte()
      'э' -> 0xfd.toByte()
      'ю' -> 0xfe.toByte()
      'я' -> 0xff.toByte()
      else -> 0x0
    }
  }
}