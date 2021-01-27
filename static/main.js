const animateCSS = (element, animation, prefix = "animate__") =>
  // We create a Promise and return it
  new Promise((resolve, reject) => {
    const animationName = `${prefix}${animation}`;
    const node = document.querySelector(element);

    node.classList.add(`${prefix}animated`, animationName);

    // When the animation ends, we clean the classes and resolve the Promise
    function handleAnimationEnd(event) {
      event.stopPropagation();
      node.classList.remove(`${prefix}animated`, animationName);
      resolve("Animation ended");
    }

    node.addEventListener("animationend", handleAnimationEnd, { once: true });
  });

const checkElement = async (selector) => {
  while (document.querySelector(selector) === null) {
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }
  return document.querySelector(selector);
};

const findAsync = async (arr, asyncCallback) => {
  const promises = arr.map(asyncCallback);
  const results = await Promise.all(promises);
  const index = results.findIndex((result) => result);
  return arr[index];
};

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      show: false,
    };
  }

  fetchData = async () => {
    const notifications_response = await axios.get("/notifications");

    const notification = await findAsync(
      notifications_response.data,
      async (notification) => {
        const isIgnored_response = await axios.get(
          `/ignore/${notification.user.username}`
        );

        return isIgnored_response.data.ignore === false;
      }
    );

    if (notification !== undefined) {
      this.setState({ username: notification.user.username, show: true });
    }

    if (this.state.username.length > 0 && notification !== undefined) {
      await axios.post(`/ignore/${notification?.user?.username}`);
    }
  };

  async componentDidMount() {
    await this.fetchData();
    setInterval(() => {
      this.fetchData();
      setTimeout(() => {
        this.setState({ username: "", show: false });
      }, 4500);
    }, 5000);
  }

  render() {
    checkElement(".main").then((selector) => {
      selector.style.display = "block";
      animateCSS(".main", "slideInRight");
    });

    setTimeout(() => {
      animateCSS(".main", "fadeOut").then((value) => {
        document.querySelector(".main").style.display = "none";
      });
    }, 3000);
    return (
      <div class="main" style={{ display: "none" }}>
        {this.state.show == true && (
          <div>
            <figure>
              <img class="logo" src="logo.svg" />
              <img class="lock" src="lock.svg" />

              <figcaption class="text">+1 SUB!</figcaption>
            </figure>
            {/* <h2 id="text">Welcome {this.state.username}</h2> */}
          </div>
        )}
        {this.state.show == false && <div></div>}
      </div>
    );
  }
}

ReactDOM.render(<App />, document.getElementById("container"));
