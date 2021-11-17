import express from "express";
import logger from "morgan";
import "./environment";
// import { router } from "./routes";
import helmet from "helmet";

const app = express();

app.use(logger("common"));
app.use(helmet());
app.use(express.json());

app.use("/", (req, res) => {
  // console.log(JSON.stringify(req.headers, null, 2));
  return res.json({ message: "hello world" });
});

app.listen(process.env.PORT, () => {
  console.log(`Server running at PORT: ${process.env.PORT}`);
});
