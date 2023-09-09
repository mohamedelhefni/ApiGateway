'use strict';

// This is an example plugin that add a header to the response

class KongPlugin {
  constructor(config) {
    this.config = config
  }

  async checkIsAuthorized() {

  }

  async access(kong) {
    let host = await kong.request.getHost()
    let method = await kong.request.getMethod()
    let path = await kong.request.getPath()
    // let path = await kong.request.getPath()
    // let method = await kong.request.getMethod()
    // if (host === undefined) {
    //   return await kong.log.err("unable to get header for request")
    // }



    console.log("Host", host)
    console.log("Path",path)
    console.log("Method", method)


    let message = this.config.message || "hello"

    // the following can be "parallel"ed
    // await Promise.all([
    //   kong.response.setHeader("x-hello-from-javascript", "Javascript says " + message + " to " + host),
    //   kong.response.setHeader("x-javascript-pid", process.pid),
    //   kong.response.exit(403, "Forbidden")
    // ])

    return kong.response.exit(403, "Forbidden")

  }
}

module.exports = {
  Plugin: KongPlugin,
  Schema: [
    { message: { type: "string" } },
  ],
  Version: '0.1.0',
  Priority: 0,
};
