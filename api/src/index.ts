import express from "express";
import logger from "morgan";
import "./environment";
// import { router } from "./routes";
import helmet from "helmet";

const app = express();

app.use(logger("dev"));
app.use(helmet());
app.use(express.json());
// app.use(router);

app.listen(process.env.PORT, () => {
  console.log(`Server running at PORT: ${process.env.PORT}`);
});
