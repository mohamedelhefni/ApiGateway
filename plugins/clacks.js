'use strict';

// This is an example plugin that add a header to the response

class KongPlugin {
  constructor(config) {
    this.config = config
  }

  async checkIsAuthorized(authProps) {
    let {token, method, path} = authProps
    let request = await fetch("http://192.168.1.3:4444/check/", {method: "POST", headers: {'Content-Type': 'application/json',Authorization: token}, body: JSON.stringify({
      token: token,
      method: method,
      path: path
    })})
    let response = await request.json()
    let resBody = {
      isAuthorized: response.is_authorized || false,
      username: response.username || ""
    }
    console.log("REs Boyd", resBody)
    return  resBody
  }

  async access(kong) {
    let method = await kong.request.getMethod()
    let path = await kong.request.getPath()

    if(path == "/auth/token/" || path == '/auth/register/') {
      console.log("it needs to return ")
      return
    }

    let token = await kong.request.getHeader('Authorization')
    let authCheck = {
      token: token,
      method: method,
      path: path
    }

    let isAuthorized = await  this.checkIsAuthorized(authCheck)
    if(!isAuthorized.isAuthorized) {
      return kong.response.exit(403, "Forbidden")
    }

    await kong.service.request.setHeader('user',  isAuthorized.username)

    // let message = this.config.message || "hello"



    // the following can be "parallel"ed
    // await Promise.all([
    //   kong.response.setHeader("x-hello-from-javascript", "Javascript says " + message + " to " + host),
    //   kong.response.setHeader("x-javascript-pid", process.pid),
    //   kong.response.exit(403, "Forbidden")
    // ])


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
