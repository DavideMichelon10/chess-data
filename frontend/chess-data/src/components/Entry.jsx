import "./Entry.css";

export default function Entry(props) {
  console.log(props)
  return (
      <div className="user-card">
            <img
              src="https://yt3.ggpht.com/ytc/AIdro_kik7i7hId8EjFMERTw3_j8ODyhoot8JF3iUJRs53htOJc=s200-c-k-c0x00ffffff-no-rj"
              alt="TheRichest"
              className="user-avatar"
            />
            <div className="user-info">
              <div className="user-header">
              {/* Se il titolo esiste, mostra il badge */}
              {props.title && <span className="title-badge">{props.title}</span>}
              <h4 className="user-name">{props.name}</h4>
              </div>
              <p className="user-handle">{props.handle}</p>
          </div>
      </div>
    );
  };
