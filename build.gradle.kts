repositories {
  mavenCentral()
  maven("https://jitpack.io")
}
plugins {
  kotlin("jvm") version "1.5.30"
  id("com.github.johnrengelman.shadow") version "7.0.0"
}
dependencies {
  implementation("io.ktor:ktor-server-netty:1.6.3")
  implementation("io.ktor:ktor-client-cio:1.6.3")
  implementation("ch.qos.logback:logback-classic:1.2.6")
  testImplementation("org.junit.jupiter:junit-jupiter:5.7.2")
  testImplementation("com.willowtreeapps.assertk:assertk-jvm:0.24")
  testImplementation("io.mockk:mockk:1.12.0")
}
tasks.compileKotlin {
  kotlinOptions.jvmTarget = "16"
  kotlinOptions.freeCompilerArgs += "-Xopt-in=kotlin.time.ExperimentalTime"
}
tasks.compileTestKotlin {
  kotlinOptions.jvmTarget = "16"
  kotlinOptions.freeCompilerArgs += "-Xopt-in=kotlin.time.ExperimentalTime"
}
tasks.test {
  useJUnitPlatform()
}
tasks.jar {
  isZip64 = true
  manifest.attributes("Main-Class" to "AppKt")
}
tasks.shadowJar {
  minimize()
}
tasks.build {
  dependsOn(tasks.shadowJar)
}
