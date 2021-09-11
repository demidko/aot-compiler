import io.ktor.application.*
import io.ktor.http.HttpStatusCode.Companion.OK
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*

fun main(args: Array<String>) {
  localhostServer().start(true)
}

fun localhostServer() = embeddedServer(Netty) {
  routing {
    get("/") { call.respond(OK) }
  }
}