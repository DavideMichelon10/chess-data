import "./Entry.css";

export default function Entry(props) {
    return (
        <div className="user-card-container">
          <h3 className="section-title">Or Select a Channel to View</h3>
    
          <div className="user-list">
            <div className="user-card">
              <img
                src="https://yt3.ggpht.com/ytc/AIdro_kik7i7hId8EjFMERTw3_j8ODyhoot8JF3iUJRs53htOJc=s200-c-k-c0x00ffffff-no-rj"
                alt="TheRichest"
                className="user-avatar"
              />
              <div className="user-info">
                <h4 className="user-name">TheRichest</h4>
                <p className="user-handle">@therichest • 14.8M subscribers</p>
              </div>
            </div>
    
            <div className="user-card">
              <img
                src="https://yt3.ggpht.com/ytc/AIdro_mVUvcD5lwHuz4aiZwH7UCnibCj1u5hquxT8rff1zTGZ6w=s200-c-k-c0x00ffffff-no-rj"
                alt="Manchester United"
                className="user-avatar"
              />
              <div className="user-info">
                <h4 className="user-name">Manchester United</h4>
                <p className="user-handle">@manutd • 9.8M subscribers</p>
              </div>
            </div>
    
            <div className="user-card">
              <img
                src="https://yt3.ggpht.com/ytc/AIdro_mPkdS1NVAv3Mz5Onf18yAZ5TlU487ov56Vx6Cd12tS0_c=s200-c-k-c0x00ffffff-no-rj"
                alt="VyacheslavOO"
                className="user-avatar"
              />
              <div className="user-info">
                <h4 className="user-name">Аид [VyacheslavOO]</h4>
                <p className="user-handle">@vyacheslavoo • 9.1M subscribers</p>
              </div>
            </div>
          </div>
        </div>
      );
    };
